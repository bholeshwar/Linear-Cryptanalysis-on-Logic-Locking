from __future__ import print_function

import ckt
import sys
import os
import random
import adapter
import argparse
import itertools
from natsort import natsorted, ns
import pickle as pkl
from onecount import onecount, sortNetwork, TWO_COMP_EQ
from find_unate import is_cubestripper

from lingeling import Solver

def hd(ys, k):
    zs = onecount(ys)
    bs = [int(ki) for ki in reversed(bin(k)[2:])]
    bs = bs + [0]*(len(zs) - len(bs))
    ws = [zi if bi else ~zi for (bi, zi) in itertools.izip(bs,zs)]
    eq = ckt.AndGate(*ws)
    return eq

def subst(eq, ps, qs):
    ws = { (pi, qi) for (pi, qi) in itertools.izip(ps, qs) }
    return eq.subst(ws)

def valToLit(v, l):
    return l if v else -l

def isPowOf2(n):
    return 0 == (n & (n-1))

def isonecounter_v1(eq, ps, k):
    subs = { pi:ckt.InputNode(pi.name + '_') for pi in ps }
    eqp = eq.subst(subs)
    ds = [(pi ^ subs[pi]) for pi in ps]
    eqHD = hd(ds, 2*k)
    y = ckt.AndGate(eq, eqp, eqHD)

    inps = [(pi, subs[pi]) for pi in ps]

    S = Solver()
    nmap = {}
    clauses = adapter.circuitToCNF(y, nmap, lambda n: S.newVar())
    for pi, qi in inps:
        S.freeze(nmap[pi])
        S.freeze(nmap[qi])
    for c in clauses:
        S.addClause(*c)
    l = nmap[y]
    S.addClause(l)


    r = S.solve()
    if not r:
        return False, None

    # gather all the input values.
    ms, ns = [], []
    for pi, qi in inps:
        ai, bi = nmap[pi], nmap[qi]
        mi = int(S.modelValue(ai))
        ni = int(S.modelValue(bi))
        ms.append(mi)
        ns.append(ni)
    
    # assert the obvious ones.
    key = {}
    for ((pi, qi), mi, ni) in itertools.izip(inps, ms, ns):
        ai, bi = nmap[pi], nmap[qi]
        if mi == ni:
            key[pi] = mi
            #S.addClause(valToLit(key[pi], ai))
            #S.addClause(valToLit(key[pi], bi))

    # now handle the rest.
    assumps = []
    for ((pi, qi), mi, ni) in itertools.izip(inps, ms, ns):
        ai, bi = nmap[pi], nmap[qi]
        if mi != ni:
            r1 = S.solve(valToLit(mi, ai), valToLit(mi, bi))
            r2 = S.solve(valToLit(ni, ai), valToLit(ni, bi))
            if r1 == True and r2 == False:
                key[pi] = mi
            elif r1 == False and r2 == True:
                key[pi] = ni
            else:
                return False, None

            #S.addClause(valToLit(key[pi], ai))
            #S.addClause(valToLit(key[pi], bi))
    ks = [key[pi] for pi in ps]
    return True, ks

def isonecounter_v2(eq, ps, k):
    S = Solver()

    subs = { pi:ckt.InputNode(pi.name + '_') for pi in ps }
    eqp = eq.subst(subs)
    y = ckt.AndGate(eq, eqp)
    inps = [(pi, subs[pi]) for pi in ps]
    ds = [(pi ^ subs[pi]) for pi in ps]

    nmap = {}
    ckt_clauses = adapter.circuitToCNF(y, nmap, lambda n: S.newVar())
    for di in ds:
        ckt_clauses += adapter.circuitToCNF(di, nmap, lambda n: S.newVar())

    zeros = []
    dlits = [nmap[di] for di in ds]
    while not isPowOf2(len(dlits)):
        zi = S.newVar()
        dlits.append(zi)
        zeros.append(zi)
    (snw_clauses, es) = sortNetwork(TWO_COMP_EQ, dlits, lambda: S.newVar())
    for pi, qi in inps:
        S.freeze(nmap[pi])
        S.freeze(nmap[qi])
    for c in zeros:
        S.addClause(-c)
    for c in itertools.chain(ckt_clauses, snw_clauses):
        S.addClause(*c)
    l = nmap[y]
    S.addClause(l)
    for i, ei in enumerate(es):
        if i < 2*k:
            S.addClause(ei)
        else:
            S.addClause(-ei)

    r = S.solve()
    if not r:
        return False, None

    # gather all the input values.
    ms, ns = [], []
    for pi, qi in inps:
        ai, bi = nmap[pi], nmap[qi]
        mi = int(S.modelValue(ai))
        ni = int(S.modelValue(bi))
        ms.append(mi)
        ns.append(ni)
    
    # assert the obvious ones.
    key = {}
    for ((pi, qi), mi, ni) in itertools.izip(inps, ms, ns):
        ai, bi = nmap[pi], nmap[qi]
        if mi == ni:
            key[pi] = mi
            #S.addClause(valToLit(key[pi], ai))
            #S.addClause(valToLit(key[pi], bi))

    # now handle the rest.
    assumps = []
    for ((pi, qi), mi, ni) in itertools.izip(inps, ms, ns):
        ai, bi = nmap[pi], nmap[qi]
        if mi != ni:
            r1 = S.solve(valToLit(mi, ai), valToLit(mi, bi))
            r2 = S.solve(valToLit(ni, ai), valToLit(ni, bi))
            if r1 == True and r2 == False:
                key[pi] = mi
            elif r1 == False and r2 == True:
                key[pi] = ni
            else:
                return False, None

            #S.addClause(valToLit(key[pi], ai))
            #S.addClause(valToLit(key[pi], bi))
    ks = [key[pi] for pi in ps]
    return True, ks

def isonecounter_v3(eq, ps, k, log):
    subs = { pi:ckt.InputNode(pi.name + '_') for pi in ps }
    eqp = eq.subst(subs)
    ds = [(pi ^ subs[pi]) for pi in ps]
    eqHD = hd(ds, 2*k)
    y = ckt.AndGate(eq, eqp, eqHD)

    inps = [(pi, subs[pi]) for pi in ps]
    S = Solver()
    nmap = {}
    clauses = adapter.circuitToCNF(y, nmap, lambda n: S.newVar())
    # freeze literals
    for pi, qi in inps:
        S.freeze(nmap[pi])
        S.freeze(nmap[qi])
    for di in ds:
        S.freeze(nmap[di])
    # add clauses.
    for c in clauses:
        S.addClause(*c)
    l = nmap[y]
    S.addClause(l)


    r = S.solve()
    if not r:
        return False, None

    # gather the first round of keys.
    assumps = []
    key = {}
    for ((pi, qi), di) in itertools.izip(inps, ds):
        ai, bi = nmap[pi], nmap[qi]
        mi = int(S.modelValue(ai))
        ni = int(S.modelValue(bi))
        if mi == ni:
            key[pi] = mi
        else:
            li = nmap[di]
            assumps.append(-li)
    
    r = S.solve(*assumps)
    if not r:
        return False, None

    # and now the second round of keys.
    for ((pi, qi), di) in itertools.izip(inps, ds):
        ai, bi = nmap[pi], nmap[qi]
        mi = int(S.modelValue(ai))
        ni = int(S.modelValue(bi))
        if mi == ni:
            key[pi] = mi

    ks = [key[pi] for pi in ps]
    if log:
        pkl.dump(eq, log)
        pkl.dump(ps, log)
        pkl.dump(ks, log)
        log.flush()
        #log.close()

    if checkKey(eq, ps, ks, k):
        return True, ks
    else:
        return False, None

def isonecounter_v4(eq, ps, k, log):
    subs = { pi:ckt.InputNode(pi.name + '_') for pi in ps }
    id_map = { pi: pi for pi in ps}
    S = Solver()
    nmap = {}
    for idx, xi in enumerate(ps):
        for xj in ps[idx + 1:]:
            new_map = id_map.copy()
            new_map[xi] = subs[xi]
            eq1 = eq.subst(new_map)
            new_map.pop(xi)

            new_map1 = new_map.copy()
            new_map1[subst[xi]] = subst[xi]
            new_map1[xj] = xi
            eq2 = eq1.subst(new_map1)
            new_map2.pop(xj)

            new_map2 = new_map1.copy()
            new_map2[xi] = xi
            new_map2[subst[xi]] = xj
            eq3 = eq2.subst(new_map2)

            or1 = eq3 ^ eq            
            #TODO add the case for the swap with negated literals

def checkKey(eq, ps, ks, k):
    qs = [~pi if ki else pi for (ki, pi) in itertools.izip(ks, ps)]
    eqP = hd(qs, k)
    miter = eq ^ eqP
    S = Solver()
    nmap = {}
    clauses = adapter.circuitToCNF(miter, nmap, lambda n: S.newVar())
    for c in clauses:
        S.addClause(*c)
    S.addClause(nmap[miter])
    r = S.solve()
    if r: return False
    else: return  True

def test(k, h):
    sys.setrecursionlimit(8192)

    ps = [ckt.InputNode('p%d' % i) for i in range(k)]
    fs = [random.randint(1, 1) for i in range(len(ps))]
    ys = [~pi if fi else pi for (fi, pi) in itertools.izip(fs, ps)]
    eq  = hd(ys, h)

    r, ks = isonecounter(eq, ps, h, None)
    if r:
        print ('fs:', fs)
        print ('ks:', ks)
        assert fs == ks
    else:
        print ('TROUBLE!')

def isonecounter(eq, ps, h, log):
    k = len(ps)
    if h*4 <= k:
        return isonecounter_v3(eq, ps, h, log)
    else:
        return isonecounter_v1(eq, ps, h)

def main():
    sys.setrecursionlimit(8192)

    parser = argparse.ArgumentParser(description='Comparator finding analysis.')
    parser.add_argument('candidates', type=str, help='file with candidate nodes.')
    parser.add_argument('--log', type=str, help='log file', default=None)
    parser.add_argument('--key', type=str, help='key output file', default=None)
    args = parser.parse_args()
    h = int(os.path.basename(args.candidates).split('_')[3])

    with open(args.candidates, 'rb') as f:
        cands = pkl.load(f)
        keys = []
        for c in cands:
            cp = ~c
            if args.log:
                logfile = open('%s_%s.dat' % (args.log, c.name), 'w')
            else:
                logfile = None

            ps = list(natsorted(c.support(), alg=ns.IGNORECASE, key=lambda n: n.name))
            r, ks = isonecounter(c, ps, h, logfile)
            if r:
                keys.append(ks)
                print ('FOUND key=%s' % ''.join(str(ki) for ki in ks))
            else:
                r, ks = isonecounter_v3(cp, ps, h, logfile)
                if r:
                    keys.append(ks)
                    print ('FOUND key=%s' % ''.join(str(ki) for ki in ks))
        if args.key: outfile = open(args.key, 'wt')
        else: outfile = sys.stdout
        for ks in keys:
            print ('key=%s' % ''.join(str(ki) for ki in ks), file=outfile)
        if args.key: outfile.close()

if __name__ == '__main__':
    # test(8, 3)
    main()


