#!/usr/bin/env python3

import random
import argparse

from collections import namedtuple

Graph = namedtuple('Graph', ['nodes', 'edges', 'max_node'])
Edge = namedtuple('Edge', ['fr', 'to', 'weight'])

def main(args):
    random.seed(args.random_seed)

    print('')
    print('working on: {}'.format(args.graph))

    graph = load_graph(args.graph)
    print('graph ({},{})'.format(len(graph.nodes), len(graph.edges)))

    print('')
    print('cut values for random vectors')
    value2cuts = {}
    for i in range(args.samples):
        random_bits = {n:random.randint(0,1) for n in graph.nodes}
        cut = cut_value(graph, random_bits)

        if not cut in value2cuts:
            value2cuts[cut] = []
        value2cuts[cut].append(random_bits)

        print('  {:>3d} - {}'.format(cut, [random_bits[b] for b in sorted(graph.nodes)]))

    max_cut = max(value2cuts.keys())
    print('')
    print('best cuts (size {})'.format(max_cut))
    for cut in value2cuts[max_cut]:
        print('  {}'.format([cut[b] for b in sorted(graph.nodes)]))
    print('')


def cut_value(graph, assignment):
    cut = 0
    for e in graph.edges:
        if assignment[e.fr] != assignment[e.to]:
            cut += 1
    return cut




def load_graph(file_name):
    nodes = set()
    edges = []
    with open(file_name, 'r') as file:
        lines = file.readlines()
        lines = [line for line in lines if not line.strip().startswith('#')]

        max_node, num_edges = [int(x) for x in lines[0].strip().split(' ')]
        #print(max_node, ' ', num_edges)
        for line in lines[1:]:
            parts = line.strip().split(' ')
            if len(parts) == 3:
                fr, to, weight = parts
                e = Edge(int(fr), int(to), float(weight))
                edges.append(e)
                nodes.add(e.fr)
                nodes.add(e.to)
                # this solver only works for max cut problems
                assert(e.weight == 1.0)
            else:
                print('the following line was scipped:\n{}'.format(line))
        assert(min(nodes) >= 0)
        assert(max(nodes)+1 == max_node)
        assert(len(edges) == num_edges)

    return Graph(nodes, edges, max_node)


def build_cli_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('graph', help='a graph data file to operate on (.qx)')
    parser.add_argument('-s', '--samples', help='the number of random configurations to try', type=int, default=25)
    parser.add_argument('-rs', '--random-seed', help='the seed of the random number generator', type=int, default=0)

    return parser


if __name__ == '__main__':
    parser = build_cli_parser()
    main(parser.parse_args())
