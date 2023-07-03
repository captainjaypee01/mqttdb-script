import secrets

def generate_aes_key():
    key_length = 32  # 32 bytes for 256-bit key
    key = secrets.token_bytes(key_length)
    return key

def export_aes_key(key, output_file):
    key_hex = key.hex()  # Convert the key to hexadecimal string
    with open(output_file, 'w') as file:
        file.write(key_hex)

CURRENT_ENV = "LOCAL"
env_output_file = {
    "LOCAL": "aes-key",
    "PROD": '/boot/wirepas/aes-key',
}
# Example usage
key = generate_aes_key()
output_file = env_output_file[CURRENT_ENV]

export_aes_key(key, output_file)