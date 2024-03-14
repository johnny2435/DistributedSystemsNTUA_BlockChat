from Crypto.PublicKey import RSA  # provided by pycryptodome

class Wallet:
    def __init__(self):
        keylength = 1024
        key = RSA.generate(keylength)
        self.private_key = key.export_key() #use .decode() to decode it
        self.public_key = key.publickey().export_key() #use .decode() to decode it
        self.utxo = 0

    def get_balance(self):
        return self.utxo