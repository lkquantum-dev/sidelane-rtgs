#!/usr/bin/env python3
"""清除 ELF .so 的 PT_GNU_STACK 可执行标志(PF_X),解决容器内
'cannot enable executable stack as shared object requires' 加载失败。不改变库功能。
用法: python3 clear_execstack.py <path-to-.so>
"""
import sys, struct

def patch(path):
    d = bytearray(open(path, 'rb').read())
    assert d[:4] == b'\x7fELF', "不是 ELF"
    assert d[4] == 2, "不是 ELF64"
    assert d[5] == 1, "不是小端"
    e_phoff = struct.unpack_from('<Q', d, 0x20)[0]
    e_phentsize = struct.unpack_from('<H', d, 0x36)[0]
    e_phnum = struct.unpack_from('<H', d, 0x38)[0]
    PT_GNU_STACK = 0x6474e551
    changed = False
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type = struct.unpack_from('<I', d, off)[0]
        if p_type == PT_GNU_STACK:
            p_flags = struct.unpack_from('<I', d, off + 4)[0]
            print("PT_GNU_STACK flags = 0x%x (%s)" % (p_flags, "RWX 可执行栈" if p_flags & 1 else "不可执行"))
            if p_flags & 0x1:
                struct.pack_into('<I', d, off + 4, p_flags & ~0x1)
                changed = True
                print("  -> 已清 PF_X,新 flags = 0x%x" % (p_flags & ~0x1))
    if changed:
        open(path, 'wb').write(d)
        print("已写回:", path)
    else:
        print("无需修改(GNU_STACK 已不可执行)")
    return changed

if __name__ == '__main__':
    patch(sys.argv[1])
