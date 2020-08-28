import os
import ckt
import sys
import time
import adapter
import argparse
import readbench

from natsort import natsorted, ns
from find_comparators import is_comparator
from detonecounter import isonecounter_v3, isonecounter_v2, isonecounter_v1
from find_unate import is_cubestripper

def find_comps(gates):
    support = set()
    tuples  = set()
    for gate in gates:
        if is_comparator(gate):
            gsup = gate.support()
            lsup = list(gsup)
            lsup.sort(key = lambda n: n.is_keyinput())
            tuples.add(tuple(lsup))
            support = support.union(gsup)
    return support, tuples

def isonecounter(eq, ps, h, log, alg):
    k = len(ps)
    if h == 0:
        return is_cubestripper(eq, ps)
    # h != 0
    if alg == 1:
        return isonecounter_v1(eq, ps, h)
    elif alg == 3:
        assert (h*4 <= k)
        return isonecounter_v3(eq, ps, h, log)
    else:
        raise ValueError ('Invalid algorithm: %d' % log)

def main(argv):
    sys.setrecursionlimit(8192)

    cpu_times_1 = time.clock()

    parser = argparse.ArgumentParser(description='Decrypt an encrypted bench file')
    parser.add_argument('bench', type=str, help='bench file to analyze.')
    parser.add_argument('--log', type=str, help='log file', default=None)
    parser.add_argument('--key', type=str, help='key output file', default=None)
    parser.add_argument('--alg', type=int, help='detection algorithm')
    args = parser.parse_args()
    # h = 0
    h = int(os.path.basename(args.bench).split('_')[3])
    if args.alg is None and h == 0:
        args.alg = 1
    jobname = '%s/%d' % (os.path.basename(args.bench), args.alg)

    cmdline_str = ' '.join('%s' % arg for arg in argv)
    print ('attempting to decrypt %s; with alg: %d' % (args.bench, args.alg))
    print ('[%s] command_line: %s' % (jobname, cmdline_str))

    inputs, outputs, node_map = readbench.readBenchFile(args.bench)
    gates = set(node_map[n] for n in node_map)
    ckt.computeLevels(gates)

    support, tuples = find_comps(gates)  

    if args.log is not None:
        logfile = open('%s' % (args.log), 'w')
    else:
        logfile = sys.stdout
    
    keyinputs = [inp for inp in support if inp.is_keyinput()]
    cktinputs = [inp for inp in support if not inp.is_keyinput()]
    for (ckti, keyi) in natsorted(tuples, alg=ns.IGNORECASE, key=lambda t: t[0].name):
        logfile.write('%-20s %-20s\n' % (ckti.name, keyi.name))

    print ('[%s] found %d comparators' % (jobname, len(tuples)))

    inputset = set(cktinputs)
    logfile.write('# of ckt inputs : %d\n' % len(inputset))
    logfile.write('# of gates      : %d\n' % len(gates))
    logfile.flush()

    candidates = []
    for i, g in enumerate(gates):
        gsupp = g.support()
        if gsupp == inputset:
            logfile.write('%s (%5d/%5d @ %d)\n' % (g.name, i+1, len(gates), g.level))
            logfile.flush()
            candidates.append(g)

    logfile.write('# of candidates : %d\n' % len(candidates))
    print('[%s] found %s candidates' % (jobname, len(candidates)))

    keys = set()
    for c in candidates:
        logfile.write('processing gate: %s\n' % c.name)
        cp = ~c
        ps = list(natsorted(c.support(), alg=ns.IGNORECASE, key=lambda n: n.name))
        r, ks = isonecounter(c, ps, h, None, args.alg)
        if r:
            keys.add(tuple(ks))
            logfile.write('[1] FOUND key=%s\n' % ''.join(str(ki) for ki in ks))
            logfile.flush()
        else:
            r, ks = isonecounter(cp, ps, h, None, args.alg)
            if r:
                keys.add(tuple(ks))
                logfile.write('[2] FOUND key=%s\n' % ''.join(str(ki) for ki in ks))
                logfile.flush()

    print ('[%s] found %d key(s)' % (jobname, len(keys)))

    if args.key: keyoutfile = open(args.key, 'wt')
    else: keyoutfile = sys.stdout
    for ks in keys:
        keystr = ''.join(str(ki) for ki in ks)
        keyoutfile.write('key=%s\n' % keystr)
        print ('[%s] key=%s' % (jobname, keystr))

    cpu_times_2 = time.clock()
    logfile.write('cpu_time %.1f\n' % (cpu_times_2 - cpu_times_1))
    logfile.flush()

    if args.key: keyoutfile.close()
    if args.log: logfile.close()
if __name__ == '__main__':
    main(sys.argv)
