import hashlib
from Crypto.Signature import pkcs1_15 # provided by pycryptodome
from Crypto.PublicKey import RSA 
from Crypto.Hash import SHA256

class Transaction:
    def __init__(self, sender_address, receiver_address, type_of_transaction, amount, message, nonce, transaction_id, signature):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.type_of_transaction = type_of_transaction
        self.amount = amount
        self.message = message
        self.nonce = nonce
        self.transaction_id = self.calculate_transaction_id()
        self.signature = None
        #self.signature = self.sign_transaction(sender_private_key)

    def sign_transaction(self, sender_private_key):
        signer = pkcs1_15.new(RSA.import_key(sender_private_key))
        return signer.sign(self.transaction_id)

    def calculate_transaction_id(self):
        data = {
            'sender_address': self.sender_address,
            'receiver_address': self.receiver_address,
            'type_of_transaction': self.type_of_transaction,
            'amount': self.amount,
            'message': self.message,
            'nonce': self.nonce
        }
        return hashlib.sha256(str(data).encode()).hexdigest()
    
    def verify_signature(self):
        """
        Verify the signature of a transaction using the sender's public key.

        Args:
        - transaction_id: The hash of the transaction to be verified.
        - signature: The signature to be verified.
        - sender_public_key: The public key of the sender.

        Returns:
        - True if the signature is valid, False otherwise.
        """
        verifier = pkcs1_15.new(RSA.import_key(self.sender_address))
        h = SHA256.new(self.transaction_id)
        try:
            verifier.verify(h, self.signature)
            return True
        except (ValueError, TypeError):
            return False