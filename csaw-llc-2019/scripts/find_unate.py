import readbench
import ckt
import sys
import adapter
from solver import Solver

def is_unate(gate):
    s = Solver()
    supports = gate.support()
    #print supports
    def newVar(n):
        return s.newVar()

    for inp in supports:
        s.push()
        node_to_literal_0 = {}
        node_to_literal_1 = {}
        for sup in supports:
            if sup != inp:
                node_to_literal_0[sup] = newVar(0)
                node_to_literal_1[sup] = node_to_literal_0[sup]

        ckt1 = ckt.NotGate(gate)
        ckt_cnf_0 = adapter.circuitToCNF(gate, node_to_literal_0, newVar)
        ckt_cnf_1 = adapter.circuitToCNF(gate, node_to_literal_1, newVar)
        for clause in ckt_cnf_0 + ckt_cnf_1:
            s.addClause(*clause)
        # Check counter example for positive unateness
        r1 = s.solve(-node_to_literal_0[inp], node_to_literal_1[inp], node_to_literal_0[gate], -node_to_literal_1[gate])
        if r1:
            # Check counter example for negative unateness
            r2 = s.solve(-node_to_literal_0[inp], node_to_literal_1[inp], -node_to_literal_0[gate], node_to_literal_1[gate])
            if r2:
                return False

        s.pop()
    return True

def is_cubestripper(gate, ps):
    # solver object
    s = Solver()

    # new variable.
    def newVar(n): return s.newVar()

    unates = []
    for inp in ps:
        s.push()
        # create clauses.
        node_to_literal_0 = {}
        node_to_literal_1 = {}
        for sup in ps:
            if sup != inp:
                node_to_literal_0[sup] = newVar(0)
                node_to_literal_1[sup] = node_to_literal_0[sup]

        ckt1 = ckt.NotGate(gate)
        ckt_cnf_0 = adapter.circuitToCNF(gate, node_to_literal_0, newVar)
        ckt_cnf_1 = adapter.circuitToCNF(gate, node_to_literal_1, newVar)
        for clause in ckt_cnf_0 + ckt_cnf_1:
            s.addClause(*clause)
        # Check counter example for positive unateness
        r1 = s.solve(-node_to_literal_0[inp], node_to_literal_1[inp], node_to_literal_0[gate], -node_to_literal_1[gate])
        if r1:
            # Check counter example for negative unateness
            r2 = s.solve(-node_to_literal_0[inp], node_to_literal_1[inp], -node_to_literal_0[gate], node_to_literal_1[gate])
            if r2:
                return False, None
            else:
                unates.append(0)
        else:
            unates.append(1)
        s.pop()
    return True, unates

def main(argv):
    test()
    unates = []
    for arg in argv[1:]:
        inputs, outputs, node_map = readbench.readBenchFile(arg)
        gates = set(node_map[n] for n in node_map)
        # compute toposort levels.
        ckt.computeLevels(gates)
        # now check unateness
        for gate in gates:
            if not gate.is_input():
                if is_unate(gate):
                    unates.append(gate)
        for u in sorted(unates, key=lambda g:(g.level, g.name)):
            print ('%s %d' % (u.name, u.level))


if __name__ == '__main__':
    main(sys.argv)

