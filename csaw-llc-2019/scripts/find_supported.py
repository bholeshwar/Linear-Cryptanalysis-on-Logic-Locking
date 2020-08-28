import readbench
import ckt
import sys
import adapter
import argparse
import pickle

def main():
    parser = argparse.ArgumentParser(description='Comparator finding analysis.')
    parser.add_argument('bench', type=str, help='bench file to analyze.')
    parser.add_argument('--support', type=str, help='input file with support nodes.')
    parser.add_argument('--candidates', type=str, help='output file for candidate nodes.')
    args = parser.parse_args()

    sys.setrecursionlimit(10000)
    inputs, outputs, node_map = readbench.readBenchFile(args.bench)
    gates = set(node_map[n] for n in node_map)
    ckt.computeLevels(gates)
        
    with open(args.support, 'r') as f:
        keyinputs = pickle.load(f)
        cktinputs = pickle.load(f)
        tuples = pickle.load(f)

    inputset = set(cktinputs)
    print ('# of ckt inputs : %d' % len(inputset))
    print ('# of gates      : %d' % len(gates))

    candidates = []
    for i, g in enumerate(gates):
        gsupp = g.support()
        if gsupp == inputset:
            print ('%s (%5d/%5d @ %d)' % (g.name, i+1, len(gates), g.level))
            candidates.append(g)

    print ('# of candidates : %d' % len(candidates))
    with open(args.candidates, 'wt') as f:
        pickle.dump(candidates, f)

if __name__ == '__main__':
    main()
