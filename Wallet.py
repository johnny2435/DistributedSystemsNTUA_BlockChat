from Crypto.PublicKey import RSA  # provided by pycryptodome

class Wallet:
    def __init__(self):
        keylength = 1024
        key = RSA.generate(keylength)
        self.private_key = key.export_key() #use .decode() to decode it
        self.public_key = key.publickey().export_key() #use .decode() to decode it
        self.utxos = {}

    def get_public_key(self):
        # Return the public key
        return self.public_key

    def get_private_key(self):
        # Return the private key
        return self.private_key

    def get_balance(self):
        # Calculate the wallet balance
        return sum(self.utxos.values())
    
    def add_utxo(self, transaction_id, amount):
        # Add a UTXO to the wallet
        self.utxos[transaction_id] = amount

