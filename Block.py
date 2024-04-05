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

    def hash(self):
        block_dictionary = self.block_dict()
        block_json = json.dumps(block_dictionary)
        return hashlib.sha256(str(block_json).encode()).hexdigest()

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def block_dict(self):
        block_dictionary = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [transaction.to_dict() for transaction in self.transactions],
            'validator': self.validator,
            'previous_hash': self.previous_hash
        }
        return block_dictionary
