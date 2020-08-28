from __future__ import print_function

import sys
import ckt
import adapter

from argparse import ArgumentParser
from readbench import readBenchFile
from solver import Solver

def is_xnor(n):
    support = n.support()
    if len(support) != 2:
        return False
    support = list(support)
    support.sort(key = lambda n: n.is_keyinput())
    if support[0].is_keyinput() or (not support[1].is_keyinput()):
        return False
    x0, x1 = support[0], support[1]
    miter = ckt.NotGate(n ^ (x0 ^ x1))
    nmap = {}
    S = Solver()
    clauses = adapter.circuitToCNF(miter, nmap, lambda n: S.newVar())
    for cl in clauses:
        S.addClause(*cl)
    r1 = S.solve(nmap[miter])
    if r1 == False: 
        return True
    else:
        return False

def is_fru(tuples, node):
    mit = ckt.Const0Node()
    nsupp = node.support()
    isupp = set()
    seltuples = []
    for (n, ci, ki) in tuples:
        if ci in nsupp and ki in nsupp:
            isupp.add(ci)
            isupp.add(ki)
            seltuples.append((ci, ki))

    print  (len(nsupp), len(isupp))
    print (nsupp)
    print (isupp)
    assert isupp == nsupp
    print ('# of pairs of inputs in support: ' % len(seltuples))
    for (ci, ki) in seltuples:
        eq = (ci ^ ki)
        mit = mit | eq
    comp = ckt.NotGate(mit)
    miter = (node ^ comp)
    S = Solver()
    nmap = {}
    clauses = adapter.circuitToCNF(miter, nmap, lambda n: S.newVar())
    for cl in clauses:
        S.addClause(*cl)
    r1 = S.solve(nmap[miter])
    if r1 == False: return True
    r2 = S.solve(-nmap[miter])
    if r2 == False: return True


def main():
    sys.setrecursionlimit(8192)

    prog_desc = 'Strip the functionality restoration unit (FRU) from SFLL locked netlists.'
    parser = ArgumentParser(description=prog_desc)
    parser.add_argument('bench', type=str, help='BENCH file to analyze.')
    parser.add_argument('--log', type=str, help='File with log output.')
    args = parser.parse_args()

    inputs, outputs, node_map = readBenchFile(args.bench)
    # ckt.computeFanouts(node_map)
    gates = set(node_map[n] for n in node_map)
    ckt.computeLevels(gates)

    print ('# of inputs     : %5d' % len(inputs))
    print ('# of outputs    : %5d' % len(outputs))
    print ('# of gates      : %5d' % len(gates))

    tuples = []
    support = set()
    for g in gates:
        if is_xnor(g):
            gsup = g.support()
            support = support.union(gsup)
            lsup = list(gsup)
            lsup.sort(key = lambda n: n.is_keyinput())
            t = (g,) + tuple(lsup)
            tuples.append(t)
            
    tuples.sort(key = lambda t: t[2].name)
    for t in tuples:
        print ('%15s %15s %15s' % (t[0].name, t[1].name, t[2].name))

    for g in gates:
        gsup = g.support()
        intsct = gsup.intersection(support)
        cnt = len(intsct)
        if cnt >= 70 and g.level <= 15:
            print (g.name, g.level, cnt)
            print (is_fru(tuples, g))

if __name__ == '__main__':
    main()
