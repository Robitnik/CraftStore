from cryptography.fernet import Fernet
import base64

class FernetEncryptor:
    default_key = b'MXqRtY6gdGWH7bExUdtm5ZSc2-s4g7vKQxoZD-9_23U='
    def __init__(self, key=default_key):
        self.key = key
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, plaintext):
        ciphertext = self.cipher_suite.encrypt(plaintext.encode())
        return ciphertext.decode()

    def decrypt(self, ciphertext):
        plaintext = self.cipher_suite.decrypt(ciphertext.encode())
        return plaintext.decode()


