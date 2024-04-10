from Crypto.PublicKey import RSA  # provided by pycryptodome

#public keys are encoded
class Wallet:
    def __init__(self):
        keylength = 1024
        key = RSA.generate(keylength)
        self.private_key = key.export_key() #use .decode() to decode it
        self.public_key = key.publickey().export_key() #use .decode() to decode it
        self.utxos = []
        self.utxos_soft = []
        self.utxos_soft_block = []

    def get_public_key(self):
        # Return the public key
        return self.public_key

    def get_balance(self):
      balance = 0
      for tx in self.utxos:
        if tx.address == self.public_key:
          balance += tx.amount
      return balance

    def get_balance_soft(self):
      balance = 0
      for tx in self.utxos_soft:
        if tx.address == self.public_key:
          balance += tx.amount
      return balance
