import random

from collections import namedtuple

Graph = namedtuple('Graph', ['nodes', 'edges', 'max_node'])
Edge = namedtuple('Edge', ['fr', 'to', 'weight'])

json_dumps_kwargs = {
    'sort_keys':True,
    'indent':2,
    'separators':(',', ': ')
}

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


def remap(graph):
    nodes = set(range(len(graph.nodes)))
    new2org = {}
    org2new = {}
    for i, idx in enumerate(sorted(graph.nodes)):
        new2org[i] = idx
        org2new[idx] = i

    edges = [Edge(org2new[e.fr], org2new[e.to], e.weight) for e in graph.edges]

    return Graph(nodes, edges, max(nodes)+1), new2org


def cut_value(graph, assignment):
    cut = 0
    for e in graph.edges:
        if assignment[e.fr] != assignment[e.to]:
            cut += 1
    return cut


def frange(start, stop, steps, include_start=True):
    inc = (stop-start)/float(steps)
    i = start
    if not include_start:
        i += inc
    while i < stop:
        yield i
        i += inc


# Python 2 compatible version
def dfs(indexes, values, assignment):
    if len(indexes) == 0:
        yield assignment
    else:
        indexes_next = set(indexes)
        index = indexes_next.pop()
        for value in values[index]:
            assignment[index] = value
            #yield from dfs(indexes_next, assignment) # python3 only
            for state in dfs(indexes_next, values, assignment):
                yield state



# turns a string encoding of bits into an array of ints
# reverses the order because bit strings are given in reverse for some reason...
def str2vals(string):
    vals = list(string)
    vals.reverse()
    return [int(v) for v in vals]


def cut_dist(graph, counts):
    cut_counts = {}
    for state, count in counts.items():
        assignment = str2vals(state)
        #print('{} => {}'.format(state, assignment))
        cv = cut_value(graph, assignment)
        #print('{}'.format(cv))
        if not cv in cut_counts:
            cut_counts[cv] = 0
        cut_counts[cv] = cut_counts[cv] + count
    total_counts = sum(cut_counts.values())
    cut_dist = {cv:count/float(total_counts) for (cv,count) in cut_counts.items()}
    return cut_dist


def expected_cut(graph, counts):
    cd = cut_dist(graph, counts)
    return sum([cv*prob for (cv,prob) in cd.items()])


def rand_cut_dist(graph, samples):
    num_bits = graph.max_node
    num_states = 2**num_bits
    bit_string_template = '{0:0'+str(num_bits)+'b}'

    cut_counts = {}
    states = [random.randint(0, num_states-1) for i in range(samples)]
    for state in states:
        bit_string = bit_string_template.format(state)
        assignment = str2vals(bit_string)
        cv = cut_value(graph, assignment)
        if not cv in cut_counts:
            cut_counts[cv] = 0
        cut_counts[cv] = cut_counts[cv] + 1

    cut_dist = {cv:count/float(samples) for (cv,count) in cut_counts.items()}
    return cut_dist



