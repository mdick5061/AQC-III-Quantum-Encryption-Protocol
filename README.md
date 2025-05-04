# ECE595: Applied Quantum Computing III – Final Project

## Overview
This repository contains our final project for ECE595: Applied Quantum Computing III. We investigate and implement two quantum key distribution (QKD) protocols, BB84 and E91, and demonstrate image encryption using the generated keys. The project emphasizes quantum algorithm/software development and leverages cloud and simulator-based quantum computing resources.

## Implementations

### BB84 QKD & Quantum-Secured Image Encryption
- **Workflow:**
  1. Generate random bit-strings and bases (Alice).  
  2. Simulate BB84 transmission and measurement, sift to obtain shared key.  
  3. Use the one-time-pad key to encrypt a user-supplied image locally.  
  4. Decrypt and verify image integrity on Bob’s side.  
- **Key Files:** `bb84_image_qkd.py` (or the Jupyter notebook version)

### E91 Entanglement-Based QKD
- **Workflow:**
  1. Generate entangled Bell pairs (singlet state) via an emitter circuit.  
  2. Alice and Bob measure their halves in randomly chosen bases.  
  3. Sift measurement results to build a shared key (applying bit flips as needed).  
  4. Encrypt and decrypt an image using the resulting key.  
- **Key Files:** `e91_image_qkd.py` (or the Jupyter notebook version)

## Getting Started

### Prerequisites
- Python 3.8 or later  
- Qiskit ≥ 1.1 (`pip install qiskit qiskit-aer`)  
- NumPy (`pip install numpy`)

## Usage

1. Place an image file named `download.png` in the repository root.

2. **BB84 Image Encryption**  
   ```bash
   python bb84_image_qkd.py
   ```
   Generates a BB84 key, encrypts download.png → download.enc, then decrypts to download_decrypted.png.

3. **E91 Image Encryption**
   ```bash
   python e91_image_qkd.py
   ```
   Generates an E91-based key, encrypts download.png → download.enc, then decrypts to download_decrypted.png.

## Contributors
- Mohamed Abdelmouty  
- Michael Dick  
- Myron Tadros  
- Joseph Zullo  
