import readbench
import ckt
import sys
import adapter
import argparse
import pickle
from solver import Solver

def is_comparator(n):
    support = n.support()
    if len(support) != 2:
        return False
    support = list(support)
    support.sort(key = lambda n: n.is_keyinput())
    if support[0].is_keyinput() or (not support[1].is_keyinput()):
        return False
    x0, x1 = support[0], support[1]
    miter = n ^ (x0 ^ x1)
    nmap = {}
    S = Solver()
    clauses = adapter.circuitToCNF(miter, nmap, lambda n: S.newVar())
    for cl in clauses:
        S.addClause(*cl)
    r1 = S.solve(nmap[miter])
    if r1 == False: return True
    r2 = S.solve(-nmap[miter])
    if r2 == False: return True
    return False

def main(argv):
    parser = argparse.ArgumentParser(description='Comparator finding analysis.')
    parser.add_argument('bench', type=str, help='bench file to analyze.')
    parser.add_argument('--support', type=str, default=None, help='output file for support nodes.')
    args = parser.parse_args()

    sys.setrecursionlimit(10000)
    inputs, outputs, node_map = readbench.readBenchFile(args.bench)
    gates = set(node_map[n] for n in node_map)
    ckt.computeLevels(gates)
    support = set()
    # find the comparators.
    tuples = []
    for gate in gates:
        if is_comparator(gate):
            gsup = gate.support()
            lsup = list(gsup)
            lsup.sort(key = lambda n: n.is_keyinput())
            tuples.append(lsup)
            support = support.union(gsup)
    
    keyinputs = [inp for inp in support if inp.is_keyinput()]
    cktinputs = [inp for inp in support if not inp.is_keyinput()]
    print ('# of key inputs: %d' % len(keyinputs))
    print ('# of ckt inputs: %d' % len(cktinputs))
    if args.support:
        with open(args.support, 'wt') as f:
            pickle.dump(keyinputs, f)
            pickle.dump(cktinputs, f)
            pickle.dump(tuples, f)
    for (ckti, keyi) in tuples:
        print ('%20s %20s' % (ckti.name, keyi.name))

        # calculate overlap.
        #for gate in gates:
        #    gsupp = gate.support()
        #    gate.overlap = (len(gsupp.intersection(support)), -len(gsupp.union(support)))
        #glist = list(gates)
        #glist.sort(key=lambda g: g.overlap)
        #for g in glist:
        #    print (g.name, g.overlap)

if __name__ == '__main__':
    main(sys.argv)
