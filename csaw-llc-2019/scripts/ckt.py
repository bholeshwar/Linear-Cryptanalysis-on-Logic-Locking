name_counter = 1
class ASTNode(object):
    CONST0      = 0
    CONST1      = 1
    INPUT       = 2
    AND_GATE    = 3
    NOT_GATE    = 4
    BUF_GATE    = 5
    OR_GATE     = 6
    XOR_GATE    = 7
    XNOR_GATE   = 8
    NAND_GATE   = 9
    NOR_GATE    = 10
    MUX_GATE    = 11

    NAMES = [
        "GND",
        "VDD",
        "INPUT",
        "AND",
        "NOT",
        "BUF",
        "OR",
        "XOR",
        "XNOR",
        "NAND",
        "NOR",
        "MUX"
    ]



    # Constructor.
    def __init__(self, t):
        "Construct an abstract ASTNode. Should never be called directly."
        self.node_type = t
        self.fanins = ()
        global name_counter
        self.name = "__n%d" % name_counter
        name_counter += 1
        self.value = None
        self.hash_code = None

    # Matching functions for node types.
    def is_const0(self):
        "Is this a constant 0?"
        return self.node_type == ASTNode.CONST0
    def is_const1(self):
        "Is this a constant 1?"
        return self.node_type == ASTNode.CONST1
    def is_const(self):
        "Is this any type of constant?"
        return self.is_const0() or self.is_const1()
    def is_input(self):
        "Is this an input node?"
        return self.node_type == ASTNode.INPUT
    def is_and_gate(self):
        "Is this an and gate?"
        return self.node_type == ASTNode.AND_GATE
    def is_not_gate(self):
        "Is this a not gate?"
        return self.node_type == ASTNode.NOT_GATE
    def is_buf_gate(self):
        "Is this a buffer? (output = input)?"
        return self.node_type == ASTNode.BUF_GATE
    def is_or_gate(self):
        "Is this an or gate?"
        return self.node_type == ASTNode.OR_GATE
    def is_xor_gate(self):
        "Is this an eXclusive or gate?"
        return self.node_type == ASTNode.XOR_GATE
    def is_xnor_gate(self):
        "Is this an eXclusive nor gate?"
        return self.node_type == ASTNode.XNOR_GATE
    def is_nand_gate(self):
        "Is this a nand gate?"
        return self.node_type == ASTNode.NAND_GATE
    def is_nor_gate(self):
        "Is this a nor gate?"
        return self.node_type == ASTNode.NOR_GATE
    def is_mux(self):
        "Is this a mux?"
        return self.node_type == ASTNode.MUX_GATE

    # Operator overloading.
    def __and__(self, other):
        "Overload a & b"
        return AndGate(self, other)
    def __or__(self, other):
        "Overload a | b"
        return OrGate(self, other)
    def __invert__(self):
        "Overload ~a"
        return NotGate(self)
    def __xor__(self, other):
        "Overload a ^ b"
        return XorGate(self, other)
    def __ne__(self, other):
        "Overload a != b. Just delegates to __eq__ in subclasses."
        return not self.__eq__(other)
    def __eq__(self, other):
        "Is this node equal to 'other'?"
        if hash(self) == hash(other):
            return other.node_type == self.node_type and self.fanins == other.fanins
        else:
            return False
    def __hash__(self):
        "Hashcode for this node."
        if self.hash_code is None:
            f_hashes = tuple(hash(fi) for fi in self.fanins)
            self.hash_code = hash((self.node_type, f_hashes))
        return self.hash_code
    def __repr__(self):
        "repr just defaults to str."
        return str(self)

    # Utility methods.
    def simplify(self):
        "Simplifier: does constant propagation."
        memo = {}
        return self._simplify(memo)

    def _simplify(self, memo):
        "Simplifier memoized implementation."
        if self not in memo:
            faninsP = [fi._simplify(memo) for fi in self.fanins]
            gP = self._simplifyGate(faninsP)
            memo[self] = gP
        return memo[self]

    def _simplifyGate(self, fanins):
        return self.clone(fanins)

    def support(self):
        stack = [self]
        support = set() # Track list of support nodes.
        visited = set() # Track visited nodes.
        # This is pretty standard DFS.
        while len(stack) > 0:
            n = stack.pop()
            if n in visited: continue
            visited.add(n)
            # Add to support?
            if n.is_input(): support.add(n)
            # Visit child nodes.
            for f in n.fanins: stack.append(f)
        return support

    def transitiveFaninCone(self):
        "Find the transitive fanin cone for this node."
        stack = [self]
        visited = set()
        # This is pretty standard DFS.
        while len(stack) > 0:
            n = stack.pop()
            if n in visited: continue
            visited.add(n)
            for f in n.fanins: stack.append(f)
        return visited

    def transitiveFaninConeTuples(self):
        "Find the transitive fanin cone for this node."
        stack = [(self.name, self)]
        visited = set()
        # This is pretty standard DFS.
        while len(stack) > 0:
            (name, n) = stack.pop()
            if (name, n) in visited: continue
            visited.add((name, n))
            for f in n.fanins:
                stack.append((f.name, f))
        return visited

    def size(self):
        "The size of this circuit."
        return len(self.transitiveFaninCone())

    def __len__(self):
        "The size of this circuit."
        return len(self.transitiveFaninCone())

    def subst(self, rewrites):
        "Substitute according to the map 'rewrite'."
        memo = {}
        return self._subst(rewrites, memo)

    def _subst(self, rewrites, memo):
        "Substitute according to the map 'rewrite' with memoization."
        if self in memo:
            return memo[self]
        if self in rewrites:
            result = rewrites[self]
        else:
            fanins = tuple(fi._subst(rewrites, memo) for fi in self.fanins)
            result = self.clone(fanins)
        memo[self] = result
        assert isinstance(result, ASTNode)
        return result

class Const0Node(ASTNode):
    def __init__(self):
        "Construct a constant 0 node."
        ASTNode.__init__(self, ASTNode.CONST0)
        self.value = 0
    def __str__(self):
        "Return a string representation of this node."
        return '0'
    def clone(self, fanins):
        "Create a clone of this node."
        return Const0Node()

class Const1Node(ASTNode):
    def __init__(self):
        "Construct a constant 1 node."
        ASTNode.__init__(self, ASTNode.CONST1)
        self.value = 1
    def __str__(self):
        "Return a string representation of this node."
        return '1'
    def clone(self, fanins):
        "Create a clone of this node."
        return Const1Node()

class InputNode(ASTNode):
    def __init__(self, name):
        "Construct an input node."
        ASTNode.__init__(self, ASTNode.INPUT)
        self.name = name
    def __str__(self):
        "Return a string representation of this node."
        return self.name
    def clone(self, fanins):
        "Create a clone of this node."
        return InputNode(self.name)
    def __hash__(self):
        "Hashcode for this node."
        if self.hash_code is None:
            self.hash_code = hash((self.node_type, self.name))
        return self.hash_code
    def __eq__(self, other):
        "Is this node equal to 'other'?"
        return other.node_type == self.node_type and other.name == self.name
    def is_keyinput(self):
        "Does this name of this input start with the lower case string 'keyinput'?"
        return self.name.startswith('keyinput')

class AndGate(ASTNode):
    def __init__(self, *fanins):
        "Construct an and gate."
        ASTNode.__init__(self, ASTNode.AND_GATE)
        assert len(fanins) >= 2
        self.fanins = tuple(fanins[:])
    def __str__(self):
        "Return a string representation of this node."
        return '(%s)' % (' & '.join('%s' % str(gi) for gi in self.fanins))
    def clone(self, fanins):
        "Create a clone of this node."
        return AndGate(*fanins)
    def _simplifyGate(self, fanins):
        fanins0 = [f for f in fanins if f.is_const0()]
        faninsP = [f for f in fanins if not f.is_const1()]
        if len(fanins0) > 0: return Const0Node()
        elif len(faninsP) == 0: return Const1Node()
        elif len(faninsP) == 1: return faninsP[0]
        else: return AndGate(*faninsP)

class NotGate(ASTNode):
    def __init__(self, *fanins):
        "Construct a not gate."
        ASTNode.__init__(self, ASTNode.NOT_GATE)
        assert len(fanins) == 1
        self.fanins = tuple(fanins[:])
    def __str__(self):
        "Return a string representation of this node."
        return '~(%s)' % str(self.fanins[0])
    def clone(self, fanins):
        "Create a clone of this node."
        return NotGate(*fanins)
    def _simplifyGate(self, fanins):
        assert len(fanins) == 1
        f0 = fanins[0]
        if f0.is_const0(): return Const1Node()
        elif f0.is_const1(): return Const0Node()
        else: return NotGate(f0)

class BufGate(ASTNode):
    def __init__(self, *fanins):
        "Construct a not gate."
        ASTNode.__init__(self, ASTNode.BUF_GATE)
        assert len(fanins) == 1
        self.fanins = tuple(fanins[:])
    def __str__(self):
        "Return a string representation of this node."
        return '~(%s)' % str(self.fanins[0])
    def clone(self, fanins):
        "Create a clone of this node."
        return BufGate(*fanins)
    def _simplifyGate(self, fanins):
        assert len(fanins) == 1
        f0 = fanins[0]
        if f0.is_const0(): return Const0Node()
        elif f0.is_const1(): return Const1Node()
        else: return BufGate(f0)

class OrGate(ASTNode):
    def __init__(self, *fanins):
        "Construct an or gate."
        ASTNode.__init__(self, ASTNode.OR_GATE)
        assert len(fanins) >= 2
        self.fanins = fanins[:]
    def __str__(self):
        "Return a string representation of this node."
        return '(%s)' % (' | '.join('%s' % str(gi) for gi in self.fanins))
    def clone(self, fanins):
        "Create a clone of this node."
        return OrGate(*fanins)
    def _simplifyGate(self, fanins):
        fanins1 = [f for f in fanins if f.is_const1()]
        faninsP = [f for f in fanins if not f.is_const0()]
        if len(fanins1) > 0: return Const1Node()
        elif len(faninsP) == 0: return Const0Node()
        elif len(faninsP) == 1: return faninsP[0]
        else: return OrGate(*faninsP)


class XorGate(ASTNode):
    def __init__(self, *fanins):
        "Construct a eXclusive or gate."
        ASTNode.__init__(self, ASTNode.XOR_GATE)
        assert len(fanins) == 2
        self.fanins = tuple(fanins[:])
    def __str__(self):
        "Return a string representation of this node."
        s0 = str(self.fanins[0])
        s1 = str(self.fanins[1])
        return '(%s ^ %s)' % (s0, s1)
    def clone(self, fanins):
        "Create a clone of this node."
        return XorGate(*fanins)
    def _simplifyGate(self, fanins):
        assert len(fanins) == 2
        f0 = fanins[0]
        f1 = fanins[1]
        if f0.is_const() and f1.is_const():
            r = f0.value ^ f1.value
            if r == 0: return Const0Node()
            elif r == 1: return Const1Node()
            else: assert False
        elif f0.is_const():
            if f0.value == 0: return f1
            elif f0.value == 1: return NotGate(f1)
            else: assert False
        elif f1.is_const():
            if f1.value == 0: return f0
            elif f1.value == 1: return NotGate(f0)
            else: assert False
        else:
            return XorGate(f0, f1)

class XnorGate(ASTNode):
    def __init__(self, *fanins):
        "Construct an eXclusive nor gate."
        ASTNode.__init__(self, ASTNode.XNOR_GATE)
        assert len(fanins) == 2
        self.fanins = tuple(fanins[:])
    def __str__(self):
        fanin_str = ', '.join(str(fi) for fi in self.fanins)
        return "xnor(%s)" % (fanin_str)
    def clone(self, fanins):
        "Create a clone of this node."
        return XnorGate(*fanins)
    def _simplifyGate(self, fanins):
        assert len(fanins) == 2
        f0 = fanins[0]
        f1 = fanins[1]
        if f0.is_const() and f1.is_const():
            r = not (f0.value ^ f1.value)
            if r == 0: return Const0Node()
            elif r == 1: return Const1Node()
            else: assert False
        elif f0.is_const():
            if f0.value == 1: return f1
            elif f0.value == 0: return NotGate(f1)
            else: assert False
        elif f1.is_const():
            if f1.value == 1: return f0
            elif f1.value == 0: return NotGate(f0)
            else: assert False
        else:
            return XnorGate(f0, f1)

class NandGate(ASTNode):
    def __init__(self, *fanins):
        "Construct a nand gate."
        ASTNode.__init__(self, ASTNode.NAND_GATE)
        assert len(fanins) >= 2
        self.fanins = tuple(fanins[:])
    def __str__(self):
        fanin_str = ', '.join(str(fi) for fi in self.fanins)
        return "nand(%s)" % (fanin_str)
    def clone(self, fanins):
        "Create a clone of this node."
        return NandGate(*fanins)
    def _simplifyGate(self, fanins):
        fanins0 = [f for f in fanins if f.is_const0()]
        faninsP = [f for f in fanins if not f.is_const1()]
        if len(fanins0) > 0: return Const1Node()
        elif len(faninsP) == 0: return Const0Node()
        elif len(faninsP) == 1: return NotGate(faninsP[0])
        else: return NandGate(*faninsP)


class NorGate(ASTNode):
    def __init__(self, *fanins):
        "Construct a nor gate."
        ASTNode.__init__(self, ASTNode.NOR_GATE)
        assert len(fanins) >= 2
        self.fanins = tuple(fanins[:])
    def __str__(self):
        fanin_str = ', '.join(str(fi) for fi in self.fanins)
        return "nor(%s)" % (fanin_str)
    def clone(self, fanins):
        "Create a clone of this node."
        return NorGate(*fanins)
    def _simplifyGate(self, fanins):
        fanins1 = [f for f in fanins if f.is_const1()]
        faninsP = [f for f in fanins if not f.is_const0()]
        if len(fanins1) > 0: return Const0Node()
        elif len(faninsP) == 0: return Const1Node()
        elif len(faninsP) == 1: return NotGate(faninsP[0])
        else: return NorGate(*faninsP)

class MuxGate(ASTNode):
    def __init__(self, *fanins):
        "Construct a multiplexer."
        ASTNode.__init__(self, ASTNode.MUX_GATE)
        assert len(fanins) == 3
        self.fanins = tuple(fanins[:])
    def __str__(self):
        fanin_str = ', '.join(str(fi) for fi in self.fanins)
        return "mux(%s)" % (fanin_str)
    def clone(self, fanins):
        "Create a clone of this node."
        return MuxGate(*fanins)
    def _simplifyGate(self, fanins):
        "Simplify mux."
        [s, a, b]  = [f for f in fanins]
        if s.is_const1():
            return b
        elif s.is_const0():
            return a
        elif a.is_const0():
            return AndGate(s, b)._simplifyGate([s, b])
        else:
            return MuxGate(s, a, b)

def notEqual(n1, n2):
    return XorGate(n1, n2)

def xnor(n1, n2):
    return XnorGate(n1, n2)

def equal(n1, n2):
    return xnor(n1, n2)

def nand(*ns):
    return NandGate(*ns)

def nor(*ns):
    return NorGate(*ns)

def mux(s, a, b):
    return MuxGate(s, a, b)

def computeLevels(gates):
    for g in gates:
        g.level = 0
    
    while True:
        changed = False
        for g in gates:
            if len(g.fanins):
                levelP = max(fi.level for fi in g.fanins) + 1
            else:
                levelP = g.level
            if g.level != levelP:
                changed = True
                assert g.level < levelP
                g.level = levelP
        if not changed: break

def computeFanouts(node_map):
    for n in node_map:
        node_map[n].fanouts = set()
    changed = True
    it = 1
    while changed:
        changed = False
        for name in node_map:
            n = node_map[name]
            for fi in n.fanins:
                fi_name = fi.name
                fi_gate = node_map[fi_name]
                if n not in fi_gate.fanouts:
                    fi_gate.fanouts.add(n)
                    changed = True
        it += 1


