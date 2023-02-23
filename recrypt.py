import crcmod, argparse

jl_crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)

def jl_crypt(data, key=0xffff):
    data = bytearray(data)

    for i in range(len(data)):
        data[i] ^= key & 0xff
        key = ((key << 1) ^ (0x1021 if (key >> 15) else 0)) & 0xffff

    return bytes(data)


ap = argparse.ArgumentParser(description='JieLi SFC data recryptor')

ap.add_argument('input',
                help='Input file')

ap.add_argument('output',
                help='Output file')

ap.add_argument('srckey',
                help="Input file's key (e.g. 0xffff), anything less than zero means no decryption is done")

ap.add_argument('dstkey',
                help="Output file's key (e.g. your chip's chipkey), anything less than zero means no encryption is done")

ap.add_argument('start',
                help="Encrypted data start (i.e. start of the app_dir_head, user.app, etc)")

ap.add_argument('end',
                help="Encrypted data end (i.e. end of the encrypted blob)")

args = ap.parse_args()

srckey   = int(args.srckey, 0)
dstkey   = int(args.dstkey, 0)
encstart = int(args.start,  0)
encend   = int(args.end,    0)


with open(args.input, 'rb') as f:
    data = bytearray(f.read())

for pos in range(encstart, encend, 32):
    mxlen = min(32, encend - pos)
    chunk = data[pos:pos+mxlen]

    abspos = (pos - encstart)

    if srckey >= 0x0000:
        chunk = jl_crypt(chunk, (srckey ^ (abspos >> 2)) & 0xffff)

    if dstkey >= 0x0000:
        chunk = jl_crypt(chunk, (dstkey ^ (abspos >> 2)) & 0xffff)

    data[pos:pos+mxlen] = chunk

with open(args.output, 'wb') as f:
    f.write(data)
