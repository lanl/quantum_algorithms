#!/usr/bin/env python3

import sys, argparse, json

from math import pi
from qiskit import QuantumProgram

import common

beta_template = 'b{:02d}'
gamma_template = 'g{:02d}'

def main(args):
    print('')
    print('working on: {}'.format(args.graph))

    graph = common.load_graph(args.graph)
    print('graph ({},{})'.format(len(graph.nodes), len(graph.edges)))

    if args.remap:
        print('')
        print('remapping:')
        graph, mapping = common.remap(graph)
        for k,v in mapping.items():
            print('  {} -> {}'.format(v,k))

    print('rounds: {}'.format(args.rounds))
    print('steps: {}'.format(args.steps))
    print('shots: {}'.format(args.shots))

    beta_vals = [value for value in common.frange(0.0, args.sample_range_scale*pi, args.steps, include_start=False)]
    gamma_vals = [value for value in common.frange(0.0, args.sample_range_scale*2.0*pi, args.steps, include_start=False)]

    print('beta: {}'.format(beta_vals))
    print('gamma: {}'.format(gamma_vals))

    names = []
    values = {}

    for r in range(args.rounds):
        bn = beta_template.format(r)
        names.append(bn)
        values[bn] = beta_vals

        gn = gamma_template.format(r)
        names.append(gn)
        values[gn] = gamma_vals


    best_config = None
    best_config_value = 0

    for config in common.dfs(names, values, {}):
        #print(config)

        num_bits = graph.max_node

        qp = QuantumProgram()
        qr = qp.create_quantum_register('qr', num_bits)
        cr = qp.create_classical_register('cr', num_bits)
        qc = qp.create_circuit('qaoa', [qr], [cr])

        for i in range(num_bits):
            qc.h(qr[i])

        for r in range(args.rounds):
            beta = config[beta_template.format(r)]
            gamma = config[gamma_template.format(r)]

            for i in range(num_bits):
                qc.u3(2*beta, -pi/2, pi/2, qr[i])

            for e in graph.edges:
                qc.x(qr[e.fr])
                qc.u1(-gamma/2.0, qr[e.fr])
                qc.x(qr[e.fr])
                qc.u1(-gamma/2.0, qr[e.fr])
                qc.cx(qr[e.fr], qr[e.to])
                qc.x(qr[e.to])
                qc.u1(gamma/2.0, qr[e.to])
                qc.x(qr[e.to])
                qc.u1(-gamma/2.0, qr[e.to])
                qc.cx(qr[e.fr], qr[e.to])

        qc.measure(qr, cr)

        result = qp.execute(['qaoa'], backend='local_qasm_simulator', shots=args.shots)

        # Show the results
        #print(result)
        data = result.get_data('qaoa')
        #print(data['counts'])
        ec = common.expected_cut(graph, data['counts'])
        #print(ec)
        #print(result.get_ran_qasm('qaoa'))

        if ec > best_config_value:
            best_config = config
            best_config_value = ec

            print('')
            print('new best: {}'.format(best_config))
            print('expected cut: {}'.format(best_config_value))
            print('counts: {}'.format(data['counts']))
        else:
            sys.stdout.write('.')
            sys.stdout.flush()

        #print(nodes)
        #print(edges)

        # print_err('loading: {}'.format(args.sample_data))
        # with open(args.sample_data) as file:
        #     data = json.load(file)

        # for solution_data in data['solutions']:
        #     row = [solution_data['num_occurrences']] + solution_data['solution']
        #     print(', '.join([str(x) for x in row]))

    json_config = {
        'steps': args.steps,
        'expected_cut': best_config_value, 
        'rounds':[]
    }
    rounds = json_config['rounds']
    for r in range(args.rounds):
        beta = config[beta_template.format(r)]
        gamma = config[gamma_template.format(r)]
        rounds.append({'beta':beta, 'gamma':gamma})

    config_file = args.graph.replace('.qx', '_config_{:02d}.json'.format(args.rounds))
    print('write: {}'.format(config_file))
    with open(config_file, 'w') as file:
        file.write(json.dumps(json_config, **common.json_dumps_kwargs))


def build_cli_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('graph', help='a graph data file to operate on (.qx)')

    parser.add_argument('-rm', '--remap', help='renames given qbits to 0..n-1', action='store_true', default=False)

    parser.add_argument('-r', '--rounds', help='number of angle rounds to apply', type=int, default=1)

    parser.add_argument('-s', '--steps', help='angle discretization steps', type=int, default=3)
    parser.add_argument('-srs', '--sample-range-scale', help='reduces the total range for angle steps', type=float, default=1.0)

    parser.add_argument('-sh', '--shots', help='number of replicates for each configuration', type=int, default=1000)

    return parser


if __name__ == '__main__':
    parser = build_cli_parser()
    main(parser.parse_args())

