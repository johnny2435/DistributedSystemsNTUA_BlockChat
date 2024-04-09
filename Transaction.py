from Crypto.Signature import pkcs1_15 # provided by pycryptodome
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA 
from Crypto.Hash import SHA256
import base64
import jsonpickle

class TransactionIO:
    def __init__(self, transaction_id, address, amount):
        self.address = address
        self.amount = float(amount)
        self.transaction_id = transaction_id
    
    def print_trans(self):
        print("TransactionIO: ", self.transaction_id, ", ", self.address, ", ", \
              self.amount, "\n")
    
    def toString(self):
        return [self.transaction_id, self.address.decode(), self.amount]
    
    
    
#public keys are encoded
class Transaction:
    def __init__(self, sender_address, receiver_address, nonce, \
                 transaction_inputs, type_of_transaction, \
                 amount=0.0, message="", signature = b"None"):
        self.sender_address = sender_address #sender_public_key
        self.receiver_address = receiver_address
        self.nonce = nonce
        self.type_of_transaction = type_of_transaction
        self.transaction_inputs = transaction_inputs
        self.amount = float(amount)
        self.message = message
        self.transaction_id = self.calculate_transaction_id()
        self.transaction_outputs=[]
        if type_of_transaction == "coins":
            fee = self.amount*0.03
            change = sum([x.amount for x in transaction_inputs]) - amount - fee
            self.transaction_outputs = [TransactionIO(self.transaction_id.hexdigest(), sender_address, change),  \
                                        TransactionIO(self.transaction_id.hexdigest(), receiver_address, amount)]
        else:
            fee = len(self.message)
            change = sum([x.amount for x in transaction_inputs]) - fee
            self.transaction_outputs = [TransactionIO(self.transaction_id.hexdigest(), sender_address, change)]
          
        #signature initialised to None for all transactions except genesis transaction
        #changes when Wallet object provides private key
        self.signature = signature

  
   #Convert transaction's data to dictionary
    def to_dict(self):
      transactions = {
          'sender_address' : self.sender_address.decode(),
          'receiver_address' : self.receiver_address.decode(),
          'nonce' : self.nonce,
          'transaction_inputs' : [x.toString() for x in self.transaction_inputs],
          'type_of_transaction' : self.type_of_transaction,
          'amount' : self.amount,
          'message' : self.message,
          'signature' : base64.b64encode(self.signature).decode()
      }
      return transactions

    #calculate transaction hash
    def calculate_transaction_id(self):
      tr_inputs = str(jsonpickle.encode(self.transaction_inputs))
      block_to_byte = bytes(str(self.sender_address) + str(self.receiver_address) + str(self.amount) + self.message + tr_inputs, 'utf-8')
      return SHA256.new(block_to_byte)

  
    def sign_transaction(self, sender_private_key):
        try:
            signer = pkcs1_15.new(RSA.import_key(sender_private_key))
            self.signature = signer.sign(self.transaction_id)
        except (ValueError, TypeError) as e:
            print(f"Error signing transaction: {e}")

 
    #Verify the transaction, returns True if the verification is successful, otherwise False
    def verify_signature(self):
        try:
            pub_key = RSA.import_key(self.sender_address)
            verifier = PKCS1_v1_5.new(pub_key)
            return verifier.verify(self.transaction_id, self.signature)
        except (ValueError, TypeError) as e:
            print(f"Error verifying transaction: {e}")
            return False
