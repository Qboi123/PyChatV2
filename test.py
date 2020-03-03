from Crypto.Cipher import AES, DES, ARC4
obj = ARC4.new(b'systeem123')  # , b"SlTKeYOpHygTYkP3")  # , b"This is an IV456")
message = b"The answer is no"
ciphertext = obj.encrypt(message)
print(ciphertext)
obj2 = ARC4.new(b'systeem123')  # , b"SlTKeYOpHygTYkP3")  # , b"This is an IV456")
print(obj2.decrypt(ciphertext))
