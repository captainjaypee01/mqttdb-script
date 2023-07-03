import os
import subprocess
import getpass

def generate_ssh_key():
    # Prompt the user for input
    passphrase = getpass.getpass("Enter passphrase for the SSH key: ")
    passphrase2 = getpass.getpass("Enter same passphrase for the SSH key: ")
    if(passphrase != passphrase2):
        print("Invalid Passphrase!\n")
        return
    networkid = input("Enter network id for the SSH Key: ")
    usertype = input("Choose type of user: \n [a] smart \n [b] lingjackusr \n Choice: ")
    if(usertype != "a" and usertype != "b"):
        print("Invalid user type choice!\n")
        return
    
    user = {
        "a": "smart",
        "b": "lingjackusr"
    }.get(usertype, "")
    filename = user + "-gateway-v52-" + networkid
    comment = user + "@SMART"
    root_folder = "C:/Users/John Paul D Dala/.ssh/gateways/"
    folder = root_folder + networkid
    print("Selected user type:", user)
    print("filename:", filename)
    print("comment:", comment)
    
    # Use the current directory if no folder is specified
    if not folder:
        folder = "./ssh_key"

    # Generate the key pair
    subprocess.run(['ssh-keygen', '-t', 'rsa', '-b', '4096', '-C', comment, '-N', passphrase, '-f', folder + '/' + filename])
    # private_key = paramiko.RSAKey.generate(4096)

    # Set the passphrase
    # private_key.write_private_key_file(os.path.join(folder, filename), password=passphrase)

    # # Save the public key
    # public_key = private_key.get_base64()
    # with open(os.path.join(folder, filename + ".pub"), "w") as f:
    #     f.write(f"ssh-rsa {public_key} {comment}\n")

def main():
    generate_ssh_key()

if __name__ == '__main__':
    main()
