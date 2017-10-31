from cryptutil import *
from challenge import *
import random

####Challenge 16
key = random_aes_key()
iv = random_aes_key()
prefix = b'comment1=cooking%20MCs;userdata='
suffix = b';comment2=%20like%20a%20pound%20of%20bacon'
replace = {b'=' : b'\\=', b';' : b'\\;'}
encrypt = lambda p: aes_encrypt_cbc(p, key, iv)
encrypt_oracle = insert_encrypt_oracle(prefix, suffix, encrypt, replace=replace)
decrypt_oracle = lambda c: b';admin=true;' in aes_decrypt_cbc(c, key, iv)
payload = b'aaaaaaaaaaaaa'
