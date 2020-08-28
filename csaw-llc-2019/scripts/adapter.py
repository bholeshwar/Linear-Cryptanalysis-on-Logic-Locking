import ckt

def circuitToCNF(root_node, node2literal_map, newVar):
    """Convert a circuit into a set of clauses. node2literal_map is a map
    from nodes to literals. newVar is a function that returns a new literal.
    This could just be the solver object's newVar method."""

    def getLiteral(n):
        """Helper function that returns a literal corresponding to a node.
        It creates a new literal using newVar if one doesn't already exist."""
        if n not in node2literal_map:
            node2literal_map[n] = newVar(n)
        return node2literal_map[n]

    queue = [root_node] # queue for BFS.
    visited = set() # empty set.
    clauses = []
    while len(queue) > 0:
        n = queue.pop(0)
        assert (isinstance(n, ckt.ASTNode))
        if n in visited:
            continue
        visited.add(n)
        # get the literal for the output node.
        output_lit = getLiteral(n)
        input_lits = [getLiteral(fi) for fi in n.fanins]
        for cl in gateToCNF(n, output_lit, input_lits):
            clauses.append(cl)
        for fi in n.fanins:
            queue.append(fi)
    return clauses

def gateSetToCNF(gates, nmap, newVar):
    "Return the clauses corresponding to a set of gates."
    def getLiteral(n):
        """Helper function that returns a literal corresponding to a node.
        It creates a new literal using newVar if one doesn't already exist."""
        if n not in nmap:
            nmap[n] = newVar(n)
        return nmap[n]

    clauses = []
    for g in gates:
        oLit = getLiteral(g)
        iLits = [getLiteral(fi) for fi in g.fanins]
        clauses += gateToCNF(g, oLit, iLits)
    return clauses

def gateToCNF(g, lOut, lFanins):
    """Return a list of clauses that encode the functionality of this gate.
    lOut is the literal corresponding to the output of the gate, while lFanins
    is a list of literals that corresponds to each of the inputs of this
    gate."""
    if g.is_const0():
        return [[-lOut]]
    elif g.is_const1():
        return [[lOut]]
    elif g.is_input():
        return []
    elif g.is_and_gate():
        zeroClauses = [[fi, -lOut] for fi in lFanins]
        oneClause = [-fi for fi in lFanins] + [lOut]
        return zeroClauses + [oneClause]
    elif g.is_not_gate():
        return [[lFanins[0], lOut], [-lFanins[0], -lOut]]
    elif g.is_buf_gate():
        return [[lFanins[0], -lOut], [-lFanins[0], lOut]]
    elif g.is_or_gate():
        oneClauses = [[-fi, lOut] for fi in lFanins]
        zeroClause = lFanins + [-lOut]
        clauses = oneClauses + [zeroClause]
        return clauses
    elif g.is_xor_gate():
        x, y, z = lFanins[0], lFanins[1], lOut
        return [[x, y, -z], [-x, -y, -z], [x, -y, z], [-x, y, z]]
    elif g.is_xnor_gate():
        x, y, z = lFanins[0], lFanins[1], lOut
        return [[x, y, z], [-x, -y, z], [x, -y, -z], [-x, y, -z]]
    elif g.is_nand_gate():
        oneClauses = [[fi, lOut] for fi in lFanins]
        zeroClause = [-fi for fi in lFanins] + [-lOut]
        return oneClauses + [zeroClause]
    elif g.is_nor_gate():
        zeroClauses = [[-fi, -lOut] for fi in lFanins]
        oneClause = lFanins + [lOut]
        clauses = zeroClauses + [oneClause]
        return clauses
    elif g.is_mux():
        [s, a, b] = [lFanins[0], lFanins[1], lFanins[2]]
        y = lOut
        clauses = [
            [ s, -a,  y],
            [-s, -b,  y],
            [ s,  a, -y],
            [-s,  b, -y]
        ]
        return clauses
    else:
        raise NotImplementedError("Unknown gate: %s" % str(g))
