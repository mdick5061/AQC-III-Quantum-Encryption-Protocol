# copy code shared with BB84
import secrets, pathlib, numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
backend = AerSimulator()
rng = secrets.SystemRandom()

# — user tweakables —
IMG_PATH        = pathlib.Path('download.png')
BLOCK_SIZE      = 5
ABORT_THRESHOLD = 0.11
SAMPLE_RATE     = 0.10

if not IMG_PATH.exists():
    raise FileNotFoundError(f'Missing {IMG_PATH}. Drop an image or edit IMG_PATH.')
img_bytes  = IMG_PATH.read_bytes()
n_img_bits = len(img_bytes)*8
print(f'Image size: {len(img_bytes):,} bytes ({n_img_bits:,} bits)')

def random_bits(n):
    return (np.random.randint(2, size=n, dtype=np.uint8),
            np.random.randint(2, size=n, dtype=np.uint8))  # data, bases

# the emitter circuit emits random bits in random bases
# the emitter circuit produces 2*n bits, where the top n bits are 
# pairwise entangled with the bottom n bits using the bell minus state
# bits are entangled with the circuit: 
# -[x]-[H]-.---
#          |
# -[x]----(+)--       to produce 1/sqrt(2)( |01> - |10> )
def emitter_circuit(source_bits, source_bases): 
    size = len(source_bases)
    assert size == len(source_bits)
    qc = QuantumCircuit(2*size, name='Laser')
    for i,(bit,basis) in enumerate(zip(source_bits,source_bases)): 
        if bit: qc.x(i)
        if basis: qc.h(i)
        qc.x(i)
        qc.h(i)
    for i,(bit,basis) in enumerate(zip(source_bits,source_bases)): 
        if bit: qc.x(i+size)
        if basis: qc.h(i+size)
        qc.x(i+size)
    for i in range(size): 
        qc.cx(i,i+size)
    return qc

# alice and bob quantum circits are the same: they guess bases and measure
# we use one circuit for both
def measure(alice_bases, bob_bases): 
    size = len(alice_bases)
    qc = QuantumCircuit(2*size, name='people')
    assert size == len(bob_bases)
    for i in range(size): 
        if alice_bases[i]: qc.h(i)
        if bob_bases[i]: qc.h(i+size)

# alice and bob classically share bases after measurement
# where they guessed the same, they have opposite bits
# alice computes image xor bits, sends image clasically, and bob decrypts with xnor
