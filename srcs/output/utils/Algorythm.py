import struct

class x:
    def __init__(self, key: str):
        self.key = key.encode('utf-8')
        self.block_size = 8  # 64 bits = 8 bytes
        self.rounds = 8      # Number of rounds
        self.subkeys = self._expand_key()

    def _expand_key(self):
        # Simplified hash: XOR bytes with position
        hash_val = 0
        for i, byte in enumerate(self.key):
            hash_val ^= (byte << (i % 64)) % (2 ** 64)

        # Generate subkeys with a simpler LCG
        subkeys = []
        x = hash_val
        a, m = 0x5DEECE66D, 2 ** 64  # Simpler constants
        for _ in range(self.rounds):
            x = (a * x + 11) % m
            subkeys.append(x & 0xFFFFFFFF)  # Use 32-bit subkeys
        return subkeys

    def _initial_vector(self):
        iv = 0
        for sk in self.subkeys:
            iv ^= sk
        return iv

    def _sbox(self, byte: int, subkey: int) -> int:
        # Simplified S-box: single modulo
        return (byte ^ (subkey & 0xFF)) & 0xFF

    def _permute(self, block: int, subkey: int) -> int:
        # Simplified permutation: rotate left by subkey bits
        shift = subkey % 32
        return ((block << shift) | (block >> (32 - shift))) & 0xFFFFFFFF

    def _round_function(self, left: int, right: int, subkey: int) -> tuple:
        # Simplified chaotic function: use subkey directly
        r_prime = right ^ (subkey & 0xFFFFFFFF)
        # Apply S-box to 4 bytes of right half
        for i in range(4):
            byte = (r_prime >> (i * 8)) & 0xFF
            r_prime ^= (self._sbox(byte, subkey) << (i * 8))
        r_prime = self._permute(r_prime, subkey)
        new_left = left ^ r_prime
        new_right = right
        return new_right & 0xFFFFFFFF, new_left & 0xFFFFFFFF

    def _encrypt_block(self, block: int) -> int:
        left = (block >> 32) & 0xFFFFFFFF
        right = block & 0xFFFFFFFF
        for r in range(self.rounds):
            left, right = self._round_function(left, right, self.subkeys[r])
        return ((left & 0xFFFFFFFF) << 32) | (right & 0xFFFFFFFF)

    def _decrypt_block(self, block: int) -> int:
        left = (block >> 32) & 0xFFFFFFFF
        right = block & 0xFFFFFFFF
        for r in range(self.rounds - 1, -1, -1):
            right, left = self._round_function(right, left, self.subkeys[r])
        return ((left & 0xFFFFFFFF) << 32) | (right & 0xFFFFFFFF)

    def encrypt(self, plaintext: bytes) -> bytes:  # Change type hint to bytes
        data = plaintext  # No encode() needed
        n = len(data)
        padding_length = (self.block_size - (n % self.block_size)) % self.block_size
        data += b'\x00' * padding_length  # Simple zero padding
        assert len(data) % self.block_size == 0, f"Data length {len(data)} not a multiple of {self.block_size}"
        blocks = [struct.unpack('<Q', data[i:i + 8])[0] for i in range(0, len(data), 8)]
        iv = self._initial_vector()
        ciphertext = []
        prev = iv
        for block in blocks:
            block ^= prev
            encrypted = self._encrypt_block(block)
            ciphertext.append(encrypted)
            prev = encrypted
        return b''.join(struct.pack('<Q', c) for c in ciphertext)

    def decrypt(self, ciphertext: bytes) -> bytes:  # Changed return type to bytes
        blocks = [struct.unpack('<Q', ciphertext[i:i + 8])[0] for i in range(0, len(ciphertext), 8)]
        iv = self._initial_vector()
        plaintext_blocks = []
        prev = iv
        for block in blocks:
            decrypted = self._decrypt_block(block) ^ prev
            plaintext_blocks.append(decrypted)
            prev = block
        data = b''.join(struct.pack('<Q', b) for b in plaintext_blocks)
        return data.rstrip(b'\x00')  # Return bytes, no decode('utf-8')