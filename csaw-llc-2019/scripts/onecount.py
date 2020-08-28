from __future__ import print_function

import ckt
from solver import Solver
from adapter import circuitToCNF
import itertools

def incrementer(xs, b):
    s = []
    for i, xi in enumerate(xs):
        if i == 0:
            si = xi ^ b
            ci = xi & b
        else:
            si = xi ^ ci
            ci = xi & ci
        s.append(si)
    s.append(ci)
    return s

def onecount(xs):
    assert len(xs) > 0
    if len(xs) == 1:
        return xs
    else:
        bits_needed = (len(xs)).bit_length()
        ys = onecount(xs[:-1])
        zs = incrementer(ys, xs[-1])
        return zs[:bits_needed]

TWO_COMP_GE = 1
TWO_COMP_LE = 2
TWO_COMP_EQ = 3
def twoCompEncoding(mode, x1, x2, y1, y2):
    "Two comparators."
    assert mode

    clauses = []
    if mode & TWO_COMP_GE:
        clauses += [[-y2, x1], [-y2, x2], [-y1, x1, x2]]
    if mode & TWO_COMP_LE:
        clauses += [[-x1, y1], [-x2, y1], [-x1, -x2, y2]]
    return clauses

def mergeNetwork(mode, xs, newvar):
    clauses = []
    assert len(xs) > 1
    assert (len(xs) & (len(xs) - 1)) == 0 # pow of 2
    if len(xs) == 2:
        x1, x2 = xs[0], xs[1]
        y1, y2 = newvar(), newvar()
        clauses += twoCompEncoding(mode, x1, x2, y1, y2)
        return (clauses, [y1, y2])
    else:
        ps = xs[:len(xs) // 2]
        qs = xs[len(xs) // 2:]
        ps_odd, ps_evn = ps[0::2], ps[1::2]
        qs_odd, qs_evn = qs[0::2], qs[1::2]
        (c1, zs_odd) = mergeNetwork(mode, ps_odd + qs_odd, newvar)
        (c2, zs_evn) = mergeNetwork(mode, ps_evn + qs_evn, newvar)
        ys = []
        for zi, zj in itertools.izip(zs_evn, zs_odd[1:]):
            yi, yj = newvar(), newvar()
            clauses += twoCompEncoding(mode, zi, zj, yi, yj)
            ys += [yi, yj]
        z1 = zs_odd[0]
        z2n = zs_evn[-1]
        r = [z1] + ys + [z2n]
        assert len(r) == len(xs)
        return (c1 + c2 + clauses, r)

def sortNetwork(mode, xs, newvar):
    clauses = []
    assert len(xs) > 1
    assert (len(xs) & (len(xs) - 1)) == 0 # pow of 2
    if len(xs) == 2:
        x1, x2 = xs[0], xs[1]
        y1, y2 = newvar(), newvar()
        clauses += twoCompEncoding(mode, x1, x2, y1, y2)
        return (clauses, [y1, y2])
    else:
        ps = xs[:len(xs) // 2]
        qs = xs[len(xs) // 2:]
        (c1, ms) = sortNetwork(mode, ps, newvar)
        (c2, ns) = sortNetwork(mode, qs, newvar)
        (c3, ys) = mergeNetwork(mode, ms + ns, newvar)
        return (c1 + c2 + c3, ys)


def testSort():
    S = Solver()
    xs = [S.newVar() for i in range(8)]
    (clauses, ws) = sortNetwork(TWO_COMP_EQ, xs, lambda: S.newVar())
    for c in clauses:
        S.addClause(*c)
    tt = []
    while S.solve():
        row = []
        ms = []
        ns = []
        bc = []
        for vi in xs:
            mi = int(S.modelValue(vi))
            ms.append(mi)
            bc.append(-vi if mi else vi)
        for vi in ws:
            mi = int(S.modelValue(vi))
            ns.append(mi)
        S.addClause(*bc)
        row.append(ms)
        row.append(ns)
        tt.append(row)
        assert list(reversed(sorted(ms))) == ns
    tt.sort()
    for row in tt:
        print (row)

def test():
    xs = [ckt.InputNode('x%d' % i) for i in range(32)]
    ys = onecount(xs)
    eq4 = ckt.AndGate(~ys[0], ~ys[1], ys[2], ~ys[3])

    print (len(eq4))
    return

    S = Solver()
    nmap = {}
    clauses = circuitToCNF(eq4, nmap, lambda n: S.newVar())
    for c in clauses:
        S.addClause(*c)

    tt = []
    while S.solve():
        blockingClause = []
        row = []
        for xi in itertools.chain(reversed(xs)):
            li = nmap[xi]
            vi = S.modelValue(li)
            row.append(vi)
            if vi: blockingClause.append(-li)
            else: blockingClause.append(li)
        num_ones = sum(row)
        li = nmap[eq4]
        vi = S.modelValue(li)
        row.append(vi)
        tt.append(row)
        S.addClause(*blockingClause)
        assert (num_ones == 4) == vi
    tt.sort()
    for row in tt:
        def listToString(l):
            return ''.join(str(int(i)) for i in l)
        p1 = listToString(row[:len(xs)])
        p2 = listToString(row[len(xs):])
        print ('%s | %s ' % (p1, p2))

if __name__ == '__main__':
    testSort()

