from time import sleep, time
from colorama import Fore
import random, string
import os
from output.utils.Algorythm import x

def Crypt(binary_data, key):
    Crypter = x(key)
    print(Fore.MAGENTA + "[#]" + Fore.WHITE + " START CRYPTING...")
    start_time = time()
    cbinary_data = Crypter.encrypt(binary_data)  # Pass bytes directly
    print(Fore.MAGENTA + "[#]" + Fore.WHITE + f" FINISHED CRYPTING [{(time()-start_time):.4f}s...")
    return cbinary_data

def GenerateKey(length=8):
    exclude_chars = ['\\', '"', "'"]
    characters = string.digits + string.punctuation
    characters = ''.join([ch for ch in characters if ch not in exclude_chars])
    return ''.join(random.choices(characters, k=length))

def GetBytes():
    try:
        file_path = input(Fore.YELLOW + "[?]" + Fore.WHITE + " FilePath > ")
        with open(file_path, 'rb') as bin_file:
            binary_asm = bin_file.read()
    except FileNotFoundError:
        print(Fore.RED + "[!]" + Fore.WHITE + " BINARY NOT FOUND!")
        return GetBytes()
    return binary_asm

def MakeStub(binary_data, key):
    os.makedirs("output", exist_ok=True)
    with open("stub.py", "r") as f:
        stub_content = f.read()

    stub_content = stub_content.replace("xzxzxzxzx", repr(Crypt(binary_data, key).hex()))
    stub_content = stub_content.replace("kykykykyky", repr(key))

    with open("output/crypt.py", "w") as f:
        f.write(stub_content)

def Main():
    print(Fore.LIGHTBLUE_EX + "[*]" + Fore.WHITE + " Welcome to OnyxCrypt!")
    sleep(2)
    print(Fore.GREEN + "[+]" + Fore.WHITE + " Generating Crypt Key.")
    Key = GenerateKey()
    print(Fore.LIGHTBLUE_EX + "[*]" + Fore.WHITE + " KEY: " + Fore.LIGHTGREEN_EX + Key)
    print(Fore.GREEN + "[+]" + Fore.WHITE + " Extracting Binary Bytes.")
    binary_data = GetBytes()
    print(Fore.LIGHTBLUE_EX + "[*]" + Fore.WHITE + " Generating Stub..")
    MakeStub(binary_data, Key)
    print(Fore.GREEN + "[+]" + Fore.WHITE + " Generated Stub created at ./output/crypt.py")

if __name__ == '__main__':
    Main()