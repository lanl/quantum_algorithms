#!/usr/bin/env python3

import sys, argparse, json

from math import pi
from qiskit import QuantumProgram

import common

def main(args):
    print('')
    print('working on: {}'.format(args.graph))
    print('with configuration: {}'.format(args.config))

    graph = common.load_graph(args.graph)
    print('graph ({},{})'.format(len(graph.nodes), len(graph.edges)))

    if args.remap:
        print('')
        print('remapping:')
        graph, mapping = common.remap(graph)
        for k,v in mapping.items():
            print('  {} -> {}'.format(v,k))

    with open(args.config, 'r') as file:
        config = json.load(file)

    print('')
    print('config:')
    print('  rounds: {}'.format(len(config['rounds'])))

    num_bits = graph.max_node

    qp = QuantumProgram()
    qr = qp.create_quantum_register('qr', num_bits)
    cr = qp.create_classical_register('cr', num_bits)
    qc = qp.create_circuit('qaoa', [qr], [cr])

    for i in range(num_bits):
        qc.h(qr[i])

    for r in config['rounds']:
        beta = r['beta']
        gamma = r['gamma']

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


    print('')
    print('execute:')
    backend_name = args.backend

    if not 'local' in backend_name:
        with open('_config') as data_file:
            config = json.load(data_file)
        assert('qx_token' in config)
        assert('qx_url' in config)

        qp.set_api(config['qx_token'], config['qx_url'])
        backends = qp.available_backends()
        print('  backends found: {}'.format(backends))
        assert(backend_name in backends)
    print('  backend: {}'.format(backend_name))


    print('  shots: {}'.format(args.shots))
    result = qp.execute(['qaoa'], backend=backend_name, shots=args.shots)

    # Show the results
    #print(result)
    data = result.get_data('qaoa')

    print('')
    print('data:')
    for k,v in data.items():
        if k != 'counts':
            print('{}: {}'.format(k, v))

    print('')
    print('result:')
    print('  state dist.:')
    for i, state in enumerate(sorted(data['counts'].keys(), key=lambda x: data['counts'][x], reverse=True)):
        assignment = common.str2vals(state)
        cv = common.cut_value(graph, assignment)
        print('  {} - {} - {}'.format(cv, state, data['counts'][state]))
        if i >= 50:
            print('first 50 of {} states'.format(len(data['counts'])))
            break

    print('')
    print('  cut dist.:')
    cut_dist = common.cut_dist(graph, data['counts'])
    for i, cv in enumerate(sorted(cut_dist.keys(), reverse=True)):
        print('  {} - {}'.format(cv, cut_dist[cv]))
        if i >= 20:
            print('first 20 of {} cut values'.format(len(cut_dist)))
            break

    ec = sum([cv*prob for (cv,prob) in cut_dist.items()])
    print('  expected cut value: {}'.format(ec))

    samples = 100000
    print('')
    print('  rand cut dist. ({}):'.format(samples))
    rand_cut_dist = common.rand_cut_dist(graph, samples)
    for i, cv in enumerate(sorted(rand_cut_dist.keys(), reverse=True)):
        print('  {} - {}'.format(cv, rand_cut_dist[cv]))
        if i >= 20:
            print('first 20 of {} cut values'.format(len(rand_cut_dist)))
            break

    if args.show_qasm:
        print('')
        print(result.get_ran_qasm('qaoa'))

    #print('')


def build_cli_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('graph', help='a graph data file to operate on (.qx)')
    parser.add_argument('config', help='a config data file to use (.json)')

    parser.add_argument('-rm', '--remap', help='renames given qbits to 0..n-1', action='store_true', default=False)

    parser.add_argument('-be', '--backend', default='local_qasm_simulator', choices=['local_qasm_simulator','ibmqx2','ibmqx4','ibmqx5','ibmqx_qasm_simulator'], help='the methods for solving the quantum program')
    parser.add_argument('-sh', '--shots', help='number of replicates for each configuration', type=int, default=1024)

    parser.add_argument('-sq', '--show-qasm', help='prints executed qasm', action='store_true', default=False)

    return parser


if __name__ == '__main__':
    parser = build_cli_parser()
    main(parser.parse_args())

