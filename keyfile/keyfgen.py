import argparse, crcmod
from Cryptodome.Cipher import AES

jl_crc16 = crcmod.mkCrcFun(0x11021,     initCrc=0x0000,     rev=False)
jl_crc32 = crcmod.mkCrcFun(0x104C11DB7, initCrc=0x26536734, rev=True)

################################################################################

def int0(s):
    return int(s, 0)

ap = argparse.ArgumentParser(description='JieLi keyfile generator')

ap.add_argument('-o', '--out', metavar='FILE',
                help='Output file (if omitted no file will be generated)')

ap.add_argument('key', type=int0,
                help='Chipkey value')

args = ap.parse_args()

################################################################################

kc_dat = bytes('%04xA000~kagami~' % args.key, 'ascii')

kc_key = b'QItaMAgAK~~|AES|'
kc_dat = AES.new(kc_key, AES.MODE_ECB).encrypt(kc_dat)

keyfile = bytes(kc_dat.hex() + kc_key.hex(), 'ascii')
keyfile += bytes('%08x' % jl_crc32(keyfile), 'ascii')

crcstring = '%04X-%08X' % (jl_crc16(keyfile), jl_crc32(keyfile))

print('CRCs:', crcstring)
print('keyfile: [%s]' % str(keyfile, 'ascii'))

if args.out is not None:
    with open(args.out, 'wb') as f:
        f.write(keyfile)
