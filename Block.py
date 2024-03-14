import json
import hashlib

class Block:
    capacity = 5
    def __init__(self, index, timestamp, transactions, validator, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.validator = validator
        self.previous_hash = previous_hash

        self.current_hash = self.hash()
    
    def hash(self):
        block_dict = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [transaction.to_dict() for transaction in self.transactions],
            'validator': self.validator,
            'previous_hash': self.previous_hash
        }
        block_json = json.dumps(block_dict)
        return hashlib.sha256(str(block_json).encode()).hexdigest()