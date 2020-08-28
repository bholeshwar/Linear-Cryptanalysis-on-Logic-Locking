import os
import sys
import numpy as np
import random
import math
import re

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
def inp_out_pairs(loc, n, inputs_given, keys_given):
	# loc = "../benchmarks/rnd/c432_enc10.bench"
	# n = 239

	inp_vars, key_vars, out_vars, variables = READFILE(loc, n)

	inp_vars.sort()
	inputs = {}
	for i in inp_vars:
		inputs[i] = inputs_given[i]

	key_vars.sort()
	keys = {}
	for i in key_vars:
		keys[i] = keys_given[i]

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

