from __future__ import print_function

import readbench
import ckt
import sys
import adapter
import argparse
import pickle

def is_adder(n, cktinputs):
    support = n.support()
    if len(support) != 2:
        return False
    support = list(support)
    support.sort(key = lambda n: n.is_keyinput())
    if support[0].is_keyinput() or support[1].is_keyinput():
        return False
    if support[0] not in cktinputs or support[1] not in cktinputs:
        return False
    return True

    x0, x1 = support[0], support[1]
    m1 = n ^ (x0 ^ x1)
    m2 = n ^ (~x0 ^ x1)
    m3 = n ^ (x0 ^ ~x1)
    m4 = n ^ (~x0 ^ ~x1)

    nmap = {}
    S = Solver()
    clauses  = adapter.circuitToCNF(m1, nmap, lambda n: S.newVar())
    clauses += adapter.circuitToCNF(m2, nmap, lambda n: S.newVar())
    clauses += adapter.circuitToCNF(m3, nmap, lambda n: S.newVar())
    clauses += adapter.circuitToCNF(m4, nmap, lambda n: S.newVar())
    for cl in clauses:
        S.addClause(*cl)
    for m in [m1, m2, m3, m4]:
        l = nmap[m]
        if S.solve(l) == False:
            return True
    return False

def main():
    parser = argparse.ArgumentParser(description='Comparator finding analysis.')
    parser.add_argument('bench', type=str, help='bench file to analyze.')
    parser.add_argument('--support', type=str, help='input file with support nodes.')
    args = parser.parse_args()

    inputs, outputs, node_map = readbench.readBenchFile(args.bench)
    gates = [node_map[n] for n in node_map]
    ckt.computeLevels(gates)
    gates.sort(key=lambda g: g.level)
        
    with open(args.support, 'r') as f:
        keyinputs = pickle.load(f)
        cktinputs = pickle.load(f)
        tuples = pickle.load(f)

    inputset = set(cktinputs)
    print ('# of ckt inputs : %d' % len(inputset))
    print ('# of gates      : %d' % len(gates))

    candidates = []
    for i, g in enumerate(gates):
        if is_adder(g, cktinputs):
            print (g)


if __name__ == '__main__':
    main()

