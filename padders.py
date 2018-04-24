from cryptography.hazmat.primitives import padding

#return pkcs#7 padded bytes
def pkcs7_pad(b, bsize):
    padder = padding.PKCS7(bsize*8).padder()
    return padder.update(b) + padder.finalize()

def pkcs7_unpad(b, bsize):
    unpadder = padding.PKCS7(bsize*8).unpadder()
    return unpadder.update(b) + unpadder.finalize()

def pkcs7_pad_16(b):
    return pkcs7_pad(b, 16)

def pkcs7_unpad_16(b):
    return pkcs7_unpad(b, 16)

def pkcs7_pad_8(b):
    return pkcs7_pad(b, 8)

def pkcs7_unpad_8(b):
    return pkcs7_unpad(b, 8)

def pkcs7_is_valid(b, bsize):
    try:
        pkcs7_unpad(b, bsize)
        return True
    except ValueError:
        return False
