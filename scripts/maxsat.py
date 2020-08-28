from sympy.logic.inference import satisfiable
import sympy as sp
import random
import math
import numpy as np

def READFILE(loc, n):
	F = open(loc, "r")
	F.readline()
	inputs = []
	keys = []
	outputs = []
	variables = {}
	for i in range(n-1):
		A = F.readline()
		B = A
		# L = A.split()
		if A[:5] == "INPUT":
			if A[:14] == "INPUT(keyinput":
				keys.append(B.replace("(", " ").replace(")", " ").split()[1])
			else:
				inputs.append(B.replace("(", " ").replace(")", " ").split()[1])
		elif A[:6] == "OUTPUT":
			outputs.append(B.replace("(", " ").replace(")", "").split()[1])
		else:
			L = B.replace("(", " ").replace(")", " ").replace(",", "").split()
			T = []
			v = L[0]
			T = L[2:]
			
			variables[v] = T
	return inputs, keys, outputs, variables

def CALCULATE(gates, vals, gate):
	L = gates[gate]
	# print( gate, L)
	if L[0] == "buf":
		return int(vals[L[1]])

	elif L[0] == "not":
		return int(not(vals[L[1]]))
	
	elif L[0] == "and":
		# return int(vals[L[1]] and vals[L[2]])
		t = vals[L[1]]
		for i in range(2, len(L)):
			t = int(t and vals[L[i]])
		return int(t)
	
	elif L[0] == "nand":
		# return int(not (vals[L[1]] and vals[L[2]]))
		t = vals[L[1]]
		for i in range(2, len(L)):
			t = int(t and vals[L[i]])
		return int(not t)
	
	elif L[0] == "or":
		# return int(vals[L[1]] or vals[L[2]])
		t = vals[L[1]]
		for i in range(2, len(L)):
			t = int(t or vals[L[i]])
		return int(t)
	
	elif L[0] == "nor":
		# return int(not (vals[L[1]] or vals[L[2]]))
		t = vals[L[1]]
		for i in range(2, len(L)):
			t = int(t or vals[L[i]])
		return int(not t)

	elif L[0] == "xor":
		# return int(vals[L[1]] ^ vals[L[2]])
		t = vals[L[1]]
		for i in range(2, len(L)):
			t = int(t ^ vals[L[i]])
		return int(t)

	elif L[0] == "xnor":
		# return int(not(vals[L[1]] ^ vals[L[2]]))
		t = vals[L[1]]
		for i in range(2, len(L)):
			t = int(t ^ vals[L[i]])
		return int(not t)

def NET(gates, values, loc, n):
	# inputs, keys, outputs, variables = READFILE(loc, n)
	L = list(gates.keys())
	L.sort()
	for i in L:
		# print(i)
		gates[i] = CALCULATE(gates, values, i)
		values[i] = gates[i]
	return values

# gives input-output pairs
def inp_out_pairs(inputs_given, keys_given):
	loc = "./c432_enc10.bench"
	n = 239

	inp_vars, key_vars, out_vars, variables = READFILE(loc, n)

	inp_vars.sort()
	inputs = {}
	m = 0
	for i in inp_vars:
		inputs[i] = inputs_given[m]
		m = m+1

	key_vars.sort()
	keys = {}
	m = 0
	for i in key_vars:
		keys[i] = keys_given[m]
		m = m + 1

	gate_vals = {}
	for i in inputs:
		gate_vals[i] = inputs[i]

	for i in keys:
		gate_vals[i] = keys[i]

	gate_vals = NET(variables, gate_vals, loc, n)

	output = {}
	for i in out_vars:
		output[i] = gate_vals[i]

	M = list(output.keys())
	M.sort()

	out = []
	for i in M:
		out.append(output[i])

	return out

def circuit(inpt, key):
	return inp_out_pairs(inpt, key)

def original(inpt):
	K = [0,1,1,0,1,0,0,0,0,1,0,1,1,1,1,0]
	# 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0
	return inp_out_pairs(inpt, K)


def binar(y, inp_bits):
	return [int(x) for x in list(bin(y).split('b')[1].zfill(inp_bits))]

def randomInp(kitne, inp_bits):
	A = []
	x = random.sample(range(0, 2**(inp_bits)), kitne)
	for i in x:
		A.append(binar(i,inp_bits))
	return A


def equations(array, coeffs):
	n = len(coeffs)
	eqn = False
	for i in range(n):
		eqn = sp.Xor(eqn, sp.And(array[i], coeffs[i]))
	eqn = sp.Xor(eqn, array[-1])
	return eqn


def solver(kitne, pairs):
	coeff = []
	for j in range(kitne):
		coeff.append(sp.Symbol('A' + str(j).zfill(len(str(kitne)))))
	T = []
	for i in pairs:
	# 	eqn = equations(i, coeff)
	# 	D = satisfiable(sp.And(T + [eqn]))
	# 	if D == False:
	# 		continue

	# 	else:	
	# 		T.append(eqn)

	# return satisfiable(sp.And(T))
		eqn = equations(i, coeff)
		T.append(eqn)

	return T


def main(n = 100):
	# inpts 36 bits, outpts 7 bits, keys 16 bits
	inputs = randomInp(n, 36)
	keys = randomInp(n, 16)
	pairs = []

	for i in range(n):
		pairs.append(inputs[i] + keys[i] + circuit(inputs[i], keys[i]))

	print(solver(59, pairs))

	return


# #main
# L = [0, 1, 1, 0, 1]
# coeff = [sp.Symbol("x1"), sp.Symbol("x2"), sp.Symbol("x3"), sp.Symbol("x4")]
# print(equations(L, coeff))

main()