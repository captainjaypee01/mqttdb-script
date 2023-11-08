from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def read_aes_key_from_file(file_path):
    with open(file_path, 'r') as file:
        aes_key_hex = file.read().strip()
    aes_key_bytes = bytes.fromhex(aes_key_hex)
    return aes_key_bytes

def encrypt_file(input_file, output_file, key):
    cipher = AES.new(key, AES.MODE_ECB)
    with open(input_file, 'rb') as file:
        plaintext = file.read()
    padded_plaintext = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    encoded_ciphertext = base64.b64encode(ciphertext)
    with open(output_file, 'wb') as file:
        file.write(encoded_ciphertext)

CURRENT_ENV = "PROD"

env_aes_file = {
    "LOCAL": "aes-key",
    "PROD": '/home/smart/wd/aes-key',
}
env_input_file = {
    "LOCAL": "network",
    "PROD": '/home/smart/wirepas/network'
}
env_output_file = {
    "LOCAL": "network.bin",
    "PROD": '/home/smart/wirepas/network.bin'
}

aes_file = env_aes_file[CURRENT_ENV]
input_file = env_input_file[CURRENT_ENV]
output_file = env_output_file[CURRENT_ENV]

key = read_aes_key_from_file(aes_file)

encrypt_file(input_file, output_file, key)