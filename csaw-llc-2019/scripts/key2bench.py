import re
import sys
from argparse import ArgumentParser, FileType
from readbench import readFileObject, writeBench
from ckt import NotGate, AndGate, OrGate

if sys.version_info[0] < 3:
    raise RuntimeError("Python 3 is needed for this script.")

key_rex = re.compile(r'key=([01]+)')
def readkeys(keyfile):
    keys = []
    for line in keyfile:
        key_match = key_rex.match(line.strip())
        assert key_match
        keystr = tuple(int(c) for c in key_match.group(1))
        keys.append(keystr)
    return keys

def createConjunct(key, keyinputs):
    assert len(key) == len(keyinputs)
    fanins = []
    for ki, inpi in zip(key, keyinputs):
        if ki == 0:
            fanins.append(NotGate(inpi))
        else:
            fanins.append(inpi)
    return AndGate(*fanins)

def createKeyFormula(keys, keyinputs):
    assert len(keys)

    fanins = []
    for key in keys:
        fanins.append(createConjunct(key, keyinputs))
    if len(fanins) == 1:
        return fanins[0]
    else:
        return OrGate(*fanins)

def main():
    desc="Program to generate a characteristic function circuit from a list of keys."
    parser = ArgumentParser(description=desc)
    parser.add_argument("keyfile", type=FileType('rt'), help='file with keys.')
    parser.add_argument('benchin', type=FileType('rt'), help='locked input bench file.')
    parser.add_argument("benchout", type=FileType('wt'), help='output bench file.')
    
    args = parser.parse_args()

    keys = readkeys(args.keyfile)
    (inputs, outputs, nodemap) = readFileObject(args.benchin)
    keyinputs = [inp for inp in inputs if inp.name.startswith('keyinput')]

    keyFormulaOut = [createKeyFormula(keys, keyinputs)]
    writeBench(args.benchout, inputs, keyFormulaOut)


if __name__ == '__main__':
    main()
