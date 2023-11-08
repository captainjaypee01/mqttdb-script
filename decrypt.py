import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def read_aes_key_from_file(file_path):
    with open(file_path, 'r') as file:
        aes_key_hex = file.read().strip()
    aes_key_bytes = bytes.fromhex(aes_key_hex)
    return aes_key_bytes

def decrypt_file(input_file, output_file, key):
    cipher = AES.new(key, AES.MODE_ECB)
    with open(input_file, 'rb') as file:
        encoded_ciphertext = file.read()

    ciphertext = base64.b64decode(encoded_ciphertext)
    decrypted_data = cipher.decrypt(ciphertext)
    plaintext = unpad(decrypted_data, AES.block_size)
    plaintext_lines = plaintext.decode().splitlines()

    for line in plaintext_lines:
        print(line)
        
    with open(output_file, 'wb') as file:
        file.write(plaintext)

CURRENT_ENV = "LOCAL"
env_aes_file = {
    "LOCAL": "aes-key",
    "PROD": '/home/smart/wd/aes-key',
}
env_input_file = {
    "LOCAL": "network.bin",
    "PROD": '/home/smart/wirepas/network.bin'
}
env_output_file = {
    "LOCAL": "decrypted.txt",
    "PROD": '/home/smart/wirepas/decrypted.txt'
}
# Example usage
aes_file = env_aes_file[CURRENT_ENV]
input_file = env_input_file[CURRENT_ENV]
output_file = env_output_file[CURRENT_ENV]

key = read_aes_key_from_file(aes_file)

print('key', key)
decrypt_file(input_file, output_file, key)
