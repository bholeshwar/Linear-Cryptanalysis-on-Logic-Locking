from __future__ import print_function

import picosat
import tempfile
import time

class Solver(object):
    def __init__(self, log=None):
        "Create a solver object."
        self.tempfile = tempfile.TemporaryFile()
        self.p = picosat.picosat_init()
        picosat.picosat_set_verbosity(self.p, 100)
        picosat.picosat_measure_all_calls(self.p)
        self.f = picosat.picosat_set_output(self.p, self.tempfile)
        self.decision_limit = -1
        self.last_sat_result = None

    def newVar(self):
        "Return a new variable."
        return picosat.picosat_inc_max_var(self.p)

    def addClause(self, *ls):
        "Add this clause to the solver."
        assert len(ls) > 0
        for l in ls:
            picosat.picosat_add(self.p, l)
        picosat.picosat_add(self.p, 0)

    def solve(self, *ls):
        "Check satisfiability under the given assumptions."
        t1 = time.time()
        for l in ls:
            picosat.picosat_assume(self.p, l)
        r = picosat.picosat_sat(self.p, self.decision_limit)
        t2 = time.time()
        if r == picosat.PICOSAT_SATISFIABLE:
            self.last_sat_result = True
            return True
        elif r == picosat.PICOSAT_UNSATISFIABLE:
            self.last_sat_result = False
            return False
        else:
            self.last_sat_result = None
            raise TimeoutError("Picosat returned unknown.")

    def modelValue(self, l, default=None):
        if self.last_sat_result is not None and not self.last_sat_result:
            raise RuntimeError('modelValue can only be invoked when solve returns SAT.')
        v = picosat.picosat_deref(self.p, l)
        if v == 1:
            return True
        elif v == -1:
            return False
        else:
            if default is None:
                raise ValueError("No assignment for literal: %d" % l)
            else:
                return default

    def push(self):
        picosat.picosat_push(self.p)

    def pop(self):
        picosat.picosat_pop(self.p)

    def reset(self):
        picosat.picosat_reset(self.p)


def test1():
    S = Solver()

    # create variables
    x = S.newVar()
    y = S.newVar()

    # add clauses to instance.
    # these clauses encode x XOR y
    S.addClause(-x, -y)
    S.addClause(x, y)

    # Solve with assumption x = 0. Should be SAT.
    r1 = S.solve(-x)
    assert r1 == 1
    print ('RESULT:', ('SAT' if r1 else 'UNSAT'))
    print ('x = %d; y = %d' % (S.modelValue(x), S.modelValue(y)))
    print

    # Let's try again, this time setting y = 0. Should be SAT again.
    r2 = S.solve(-y)
    assert r2 == 1
    print ('RESULT:', ('SAT' if r2 else 'UNSAT'))
    print ('x = %d; y = %d' % (S.modelValue(x), S.modelValue(y)))
    print

    # Solve with assumption x = y = 0. Should be UNSAT.
    r3 = S.solve(-x, -y)
    assert r3 == 0
    # print (S.modelValue(x))
    print ('RESULT:', ('SAT' if r3 else 'UNSAT'))


if __name__ == '__main__':
    test1()
