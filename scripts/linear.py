from sympy.logic.inference import satisfiable
import sympy as sp
import random
import math
import numpy as np
from numba import jit

'''
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
'''
def original(L):
	#takes as input the 7 bits of input to circuit, in order
	a1 = L[0]
	a2 = L[1]
	a3 = L[2]
	a4 = L[3]
	a5 = L[4]
	a6 = L[5]
	a7 = L[6]

	return [(a1 and a6) or (not a5) , (a2 and a3 and a4) or not(a3 and a7)]

def circuit(L, K):
	# L contains 7 bit inputs and K contains 4 bit key
	# Correct key is 0101
	a1 = L[0]
	a2 = L[1]
	a3 = L[2]
	a4 = L[3]
	a5 = L[4]
	a6 = L[5]
	a7 = L[6]
	k1 = K[0]
	k2 = K[1]
	k3 = K[2]
	k4 = K[3]

	return [((a1 ^ k1) and a6) or not(a5 ^ k3), (a2 and not(a3 ^ k2) and a6) or not( not(a3 ^ k2) and not(a7 ^ k4) ) ]

@jit
def binar(y, inp_bits):
	return [int(x) for x in list(bin(y).split('b')[1].zfill(inp_bits))]

@jit
def calculate(coeffs, values):
	val = 0
	for i in range(len(coeffs)):
		val = int(val ^ int(int(coeffs[i]) and int(values[i])))
	return int(val ^ int(values[-1]))

@jit
def bias_calculator(coeffs, texts):
	n = len(texts)
	counter = 0
	for i in range(n):
		t = calculate(coeffs, texts[i])
		if t == 0:
			counter += 1
	return counter

@jit
def generate_random(n, input_bits):
	L = []
	for i in range(n):
		inputs = np.random.randint(0, 2, input_bits)
		out = np.array(original(inputs))
		L.append(np.concatenate((inputs, out)))
	return np.array(L)

@jit
def generate_with_KEY(n, input_bits, KEY):

	L = []
	for i in range(n):
		inputs = np.random.randint(0, 2, input_bits)
		out = np.array(circuit(inputs, KEY))
		L.append(np.concatenate((inputs, out)))
	return np.array(L)


def create_table(input_bits, output_bits, key_bits, n = 10000):
	L = [] #linear approximation table
	texts = generate_random(n, input_bits)
	for i in range(2**(input_bits + output_bits)):
		print(i)
		coeffs = [int(x) for x in list(bin(i)[2:].zfill(input_bits + output_bits))]
		L.append(bias_calculator(coeffs, texts) - n/2)
	return np.array(L)


def key_counters(table, input_bits, output_bits, key_bits, nfreq = 2, n = 1000):
	#nfreq is the n-th most 
	copy = np.abs(np.array(table))
	copy[0] = 0
	for i in range(nfreq):
		idx = np.argmax(copy)
		copy[idx] = 0
	coeff = [int(x) for x in list(bin(idx)[2:].zfill(input_bits + output_bits))]
	print(coeff)
	key_freq = []

	for i in range(2**(key_bits)):
		K = [int(x) for x in list(bin(i)[2:].zfill(key_bits))]
		texts = generate_with_KEY(n, input_bits, K)
		counter = bias_calculator(coeff, texts)
		if(table[idx] < 0):
			counter = n - counter
		key_freq.append(counter)

	key_freq = np.array(key_freq)
	KEYS = np.flip(np.argsort(key_freq))
	return KEYS

@jit
def possible(coeff, input_bits, output_bits, input_frac = 0.2, output_frac = 0.2):
	count = 0
	for i in range(input_bits):
		count += coeff[i]
	if count < input_frac * input_bits:
		return 0
	count = 0
	for i in range(input_bits, input_bits + output_bits):
		count += coeff[i]
	if count < output_frac * output_bits:
		return 0
	return 1


def select_coeff(table, input_bits, output_bits):
	copy = np.abs(np.array(table))
	copy[0] = 0
	idx = np.argmax(copy)
	coeff = [int(x) for x in list(bin(idx)[2:].zfill(input_bits + output_bits))]
	copy[idx] = 0
	idx = np.argmax(copy)
	coeff = [int(x) for x in list(bin(idx)[2:].zfill(input_bits + output_bits))]
	count = 2
	while(not(possible(coeff, input_bits, output_bits))):
		copy[idx] = 0
		idx = np.argmax(copy)
		coeff = [int(x) for x in list(bin(idx)[2:].zfill(input_bits + output_bits))]
		count += 1
	return count









input_bits = 7
output_bits = 2
key_bits = 4


table = (create_table(input_bits, output_bits, key_bits))
# idx = select_coeff(table, input_bits, output_bits)
# print(idx)
print(key_counters(table, input_bits, output_bits, key_bits, 2))