import hashlib
from Crypto.Signature import pkcs1_15 # provided by pycryptodome
from Crypto.PublicKey import RSA 
from Crypto.Hash import SHA256

class Transaction:
    def __init__(self, sender_address, receiver_address, type_of_transaction, amount, \
                 message, nonce):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.type_of_transaction = type_of_transaction
        self.amount = amount
        self.message = message
        self.nonce = nonce
        self.transaction_id = self.calculate_transaction_id()
        #signature initialised to None, changes when Wallet object provides private key
        self.signature = None

    def sign_transaction(self, sender_private_key):
        try:
            signer = pkcs1_15.new(RSA.import_key(sender_private_key))
            self.signature = signer.sign(self.transaction_id)
        except (ValueError, TypeError) as e:
            print(f"Error signing transaction: {e}")

    #Convert transaction's data to dictionary
    def to_dict(self):
        data = {
            'sender_address': self.sender_address,
            'receiver_address': self.receiver_address,
            'type_of_transaction': self.type_of_transaction,
            'amount': self.amount,
            'message': self.message,
            'nonce': self.nonce
        }
        return data
    
    #Calculate hash of the transaction
    def calculate_transaction_id(self): 
        transaction_dict_str = str(self.to_dict())
        transaction_bytes = bytes(transaction_dict_str, encoding='utf-8')
        hash =  SHA256.new(transaction_bytes)
        return hash#.hexdigest()
    
############## TESTING GROUND ##############
# Create a sample transaction
sender_address = "sender_public_address"
receiver_address = "receiver_public_address"
type_of_transaction = "coins"
amount = 10
message = "Test transaction"
nonce = 1

# Placeholder private key
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

# Create a Transaction object
transaction = Transaction(sender_address, receiver_address, type_of_transaction, amount, message, nonce)

# Test the to_dict method
print("Transaction data dictionary:")
print(transaction.to_dict())
print()

# Test the calculate_transaction_id method
print("Transaction ID:")
print(transaction.calculate_transaction_id().hexdigest())
print()

# Test the sign_transaction method (using a placeholder private key)
transaction.sign_transaction(private_key)

# Print the transaction signature
print("Transaction signature:")
print(transaction.signature)