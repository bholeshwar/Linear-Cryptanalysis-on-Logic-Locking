import readbench
import ckt
import sys
import adapter
from solver import Solver

# pos: f(0, X) <= f(1, X): f(0)=1 f(1)=0
# neg: f(1, X) <= f(0, X): f(0)=0 f(1)=1

def checkUnate(S, i, f0, f1, iMap, polarity):
    assumps = []
    for inp in iMap:
        i1, i2, eq = iMap[inp]
        if inp == i:
            assumps += [-i1, i2]
        else:
            assumps += [eq]
    if polarity:
        assumps += [f0, -f1]
    else:
        assumps += [-f0, f1]
    
    r = S.solve(*assumps)
    if r == True:
        return False
    else:
        return True

def getUnateNodes(outputs):
    S = Solver()

    supports = set()
    gates = set()
    for o in outputs:
        supports = supports.union(o.support())
        gates = gates.union(o.transitiveFaninCone())
    # topo sort.
    ckt.computeLevels(gates)

    def newVar(n): return S.newVar()

    cnf = []
    nmap1 = {}
    nmap2 = {}
    cnf += adapter.gateSetToCNF(gates, nmap1, newVar)
    cnf += adapter.gateSetToCNF(gates, nmap2, newVar)
    
    iMap = {}
    for inp in supports:
        i1 = ckt.InputNode(inp.name + "__1")
        i2 = ckt.InputNode(inp.name + "__2")
        iEq = ckt.XnorGate(i1, i2)
        nmap = { i1 : nmap1[inp], i2 : nmap2[inp] }
        cnf += adapter.circuitToCNF(iEq, nmap, newVar)
        iMap[inp] = (nmap[i1], nmap[i2], nmap[iEq])

    for c in cnf: S.addClause(*c)

    unates = set()
    for gate in gates:
        if gate.is_input(): 
            continue
        f0 = nmap1[gate]
        f1 = nmap2[gate]
        unate = True
        for i in supports:
            c1 = checkUnate(S, i, f0, f1, iMap, 0)
            c2 = checkUnate(S, i, f0, f1, iMap, 1)
            if not c1 and not c2:
                unate = False
                break
        if unate:
            unates.add(gate)

    return unates

def clipContainedNodes(unates):
    unateNodes = unates.copy()
    for u in unateNodes:
        if u not in unates:
            continue
        tfc = u.transitiveFaninCone()
        for n in tfc:
            if n != u and n in unates:
                unates.remove(n)
    return unates

def test():
    #for arg in argv[1:]:
    #    inputs, outputs, node_map = readbench.readBench(arg)
    a = ckt.InputNode('a')
    b = ckt.InputNode('b')
    c = ckt.InputNode('c')
    f = a & b & c
    g = (a & b) | (~a & ~b)
    unates = getUnateNodes([f, g])
    for u in unates:
        print (u)


def main(argv):
    # test()
    for arg in argv[1:]:
        inputs, outputs, node_map = readbench.readBenchFile(arg)
        unates = getUnateNodes(outputs)
        #print len(unates)
        #print "Filename: %s" % arg
        #print "Total no. of gates: %s" % str(len(node_map.keys()))
        #print "Total no. of unate gates: %s" % str(len(unates))
        #print "Percentage unate: %s" % (float(len(unates) * 100.0 / len(node_map.keys())))

        for u in sorted(unates, key=lambda g:(g.level, g.name)):
            print ('%s %d' % (u.name, u.level))

if __name__ == '__main__':
    main(sys.argv)

