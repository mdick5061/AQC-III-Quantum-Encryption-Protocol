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
def measure_circuit(alice_bases, bob_bases): 
    size = len(alice_bases)
    qc = QuantumCircuit(2*size, name='people')
    assert size == len(bob_bases)
    for i in range(size): 
        if alice_bases[i]: qc.h(i)
        if bob_bases[i]: qc.h(i+size)

def full_quantum_circuit(source_bits, source_bases, alice_bases, bob_bases): 
    ec = emitter_circuit(source_bits, source_bases)
    return ec.compose(measure_circuit(alice_bases, bob_bases))

def hamming(a,b): return np.count_nonzero(a!=b)

def bits_to_bytes(bits):
    out = bytearray()
    for i in range(0,len(bits),8):
        byte = 0
        for j in range(8):
            if i+j < len(bits):
                byte = (byte << 1) | int(bits[i+j])
        out.append(byte)
    return bytes(out)

# alice and bob classically share bases after measurement
# where they guessed the same, they have opposite bits
# alice computes image xor bits, sends image clasically, and bob decrypts with xnor

def exec(): 
    alice_key = []
    bob_key   = []
    rounds    = 0

    while len(alice_key) < n_img_bits: 
        rounds += 1
        bits_S, bases_S = random_bits(BLOCK_SIZE)
        bases_A, bases_B = random_bits(BLOCK_SIZE)
        qc = emitter_circuit(bits_S, bases_S, bases_A, bases_B)
        compiled = transpile(qc, backend)
        result = backend.run(compiled, shots=1).result()
        bitstr = next(iter(result.get_counts()))
        measurement = np.fromiter(map(int, bitstr[::-1]), dtype=np.uint8)
        meas_A = measurement[:len(measurement)//2]
        meas_B = measurement[len(measurement)//2:]

        keep_mask = bases_A == bases_B
        sift_A = meas_A[keep_mask]
        sift_B = meas_B[keep_mask]

        alice_key.extend(sift_A.tolist())
        bob_key.extend(1^sift_B.tolist())

        print(f'Round {rounds:>3}: {len(alice_key):,}/{n_img_bits} key bits \r', end='')
    
    alice_key = np.array(alice_key[:n_img_bits], dtype=np.uint8)
    bob_key   = np.array(bob_key  [:n_img_bits], dtype=np.uint8)
    assert np.array_equal(alice_key, bob_key)
    print(f'\nKey done: {len(alice_key):,} bits')

    key_bytes = bits_to_bytes(alice_key)
    cipher    = bytes(m ^ k for m,k in zip(img_bytes, key_bytes))

    enc_path = IMG_PATH.with_suffix('.enc')
    enc_path.write_bytes(cipher)

    # Bob decrypts
    dec_bytes = bytes(c ^ k for c,k in zip(cipher, key_bytes))
    dec_path  = IMG_PATH.with_stem(IMG_PATH.stem + '_decrypted')
    dec_path.write_bytes(dec_bytes)
    assert dec_bytes == img_bytes
    print('\u2705 Success — decrypted image identical.')

if __name__ == "__main__": 
    exec()
