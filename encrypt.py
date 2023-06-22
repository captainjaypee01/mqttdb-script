from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def encrypt_file(input_file, output_file, key):
    cipher = AES.new(key, AES.MODE_ECB)
    with open(input_file, 'rb') as file:
        plaintext = file.read()
    padded_plaintext = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    encoded_ciphertext = base64.b64encode(ciphertext)
    with open(output_file, 'wb') as file:
        file.write(encoded_ciphertext)

# Example usage
input_file = 'input.txt'
output_file = 'encrypted.bin'
key = b'mysecretpassword'

encrypt_file(input_file, output_file, key)