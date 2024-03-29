import Block
import Blockchain
import time
import Transaction
import Wallet
import threading
import requests
import math
import random

random.seed(10) #move
INITIAL_STAKE = 10
CAPACITY = 5
port = ':5000'
ip = '192.168.0.1'
master_ip = '192.168.0.1'

class Node:
    def __init__(self, bootstrap = False, N=0):
        self.wallet = self.generate_wallet()
        self.transaction_pool = []
        self.chain = Blockchain.Blockchain(capacity=CAPACITY)
        self.nonce = 0
        self.minted = False
        if(bootstrap):
            self.id = 0
            self.current_id_count = 1 #id for next node
            self.ring = {self.wallet.public_key : [0, '192.168.0.1', INITIAL_STAKE]} #.decode() if u want print :P
          
            genesis_transaction = Transaction.Transaction(b'0', self.wallet.public_key,\
            self.nonce, [], "coins", amount=1000*N, signature=b'bour_gee')
            
            genesis_block = Block.Block(0, time.time(), [genesis_transaction], None, 1)
          
            self.run_block(genesis_block)
            self.chain.add_block(genesis_block)
        else:
            self.id=-1
            self.ring={}	
 

        run_trans = threading.Thread(target=self.run_trans_from_txt, daemon=True)
        run_trans.start()

    #*
    def generate_wallet(self):
        return Wallet.Wallet()

    #*
    def create_transaction(self, receiver, type_of_transaction, amount = 0, message = ""):
        transactionInputs = []
    
        for tx in self.wallet.utxos_soft:
            if tx.address == self.wallet.public_key:
                transactionInputs.append(tx)
    
        trans = Transaction.Transaction(self.wallet.public_key, receiver, self.nonce, \
                            transactionInputs, type_of_transaction, amount, message)
        self.broadcast_transaction(trans)
  
        return trans

    #*
    def sign_transaction(self, transaction):
        transaction.sign_transaction(self.wallet.private_key)
        return transaction

    #*
    def verify_signature(self, transaction):
        return transaction.verify_signature()
        
  
    def broadcast(self, obj, type):
      dict = obj.to_dict() if type != 'NewNode' else obj
      print("[Broadcast]: Broadcasting " + type + " ...")
      print("\t" + type + ": ", dict)
      for value in self.ring.values():
          #dict has items of type: {public_key: [id, ip, stake]}
          ip_bc = value[1]
          url = 'http://' + ip_bc + port + '/send'+ type
          requests.post(url, json = dict)

    #*
    def broadcast_transaction(self, tx):
        self.broadcast(tx, 'Transaction')

    #*
    def broadcast_block(self, tx):
        self.broadcast(tx, 'Block')



    #*
    def validate_transaction(self, T):
      if not T.verify_signature(): 
        print("Error: Wrong signature!\n")
        return False

      if T.sender_address == T.receiver_address:
        print("[Transaction]: ERROR: You can't send BCC/messages to yourself")
        return False
      inputs = T.transaction_inputs
      outputs = T.transaction_outputs
  
      if inputs == []:
        print("[Validation Failed]: You got no inputs bozo!")
        return False
  
      total = sum([t_in.amount for t_in in inputs])
  
      fee = T.amount * 0.03 if T.type_of_transaction == 'coins' else len(T.message)
      stake = self.ring[T.sender_address][2] #sender_address is sender public key
      if total - stake < T.amount + fee:
        print(co.colored("[ERROR]: Sender doesn't have enough money", 'red'))
        return False
  
      for t_in in inputs:
        found = False 
        for t_utxo in self.wallet.utxos_soft:
          if t_in.transaction_id == t_utxo.transaction_id and \
          t_in.address == t_utxo.address and t_in.amount == t_utxo.amount:
              found = True
        if found == False:
          print("\n")
          print("\t\t[Validation Failed]: Transaction Input didn't match UTXOs")
          print("\t\t\tTransaction that didn't match:")
          t_in.print_trans()
          print("Validation Error Message END\n")
          return False
  
      for t_out in outputs:
        if t_out.amount < 0:
          print(co.colored("[ERROR]: UTXO output has negative value", 'red'))
          return False 
  
      return True

    #in rest if capacity of pool is exceeded execute mint_block and broadcast block
    def add_transaction_to_pool(self, T): #in rest first validate then add to pool
      self.transaction_pool.append(T)
      print('Transaction added to pool')
      return
  
    #*
    def mint_block(self, prevHash):
      index = self.chain.get_last_block().index + 1
      self.validator = self.Proof_of_Stake()
      if self.id == self.validator:
        block = Block.Block(index, time.time(), [], self.id, prevHash)
        for tx in self.transaction_pool[:CAPACITY]:
          block.add_transaction(tx)
        return block
      self.minted = True #:p change it to false uwu
      return
    #in rest remove the tx from pool if block valid (in receive block)

    #*
    #called when a block is received
    def validate_block(self, B):
      if not self.minted:
        self.validator = self.Proof_of_Stake()
      self.minted = False
      print(co.colored("[ENTER]: validate_block\n", "red"))
      if not self.validator == B.validator:
        print("[EXIT]: validate_block: wrong validator\n")
        return False
      for tx in B.transactions:
        if not self.validate_transaction(tx):
          print("[EXIT]: validate_block: invalid transaction\n")
          return False
      if self.chain.get_last_block().hash() != B.previous_hash:
        print("[EXIT]: validate_block: prev hash doesn't match\n")
        return False
      for tx in B.transactions:
        self.run_transaction_local(tx)
      print("[EXIT]: validate_block: valid\n")
      return True
      
  
    #find a way to save stakes (maybe in ring)
    def Proof_of_Stake(self):
        total_stakes = sum([v[2] for v in self.ring.values()])
        if total_stakes == 0:
            return False
  
        stake_target = random.uniform(0, total_stakes)
        current = 0
        l = list(self.ring.values())
        l.sort()
        for node_id, _, stake_amount in l:
            current += stake_amount
            if current >= stake_target:
                validator = node_id
                break
  
        return validator



    def run_transaction(self, T, validator):
        if T.receiver_address == 0:
            self.ring[T.sender_address][2] = T.amount
            return

        transaction_inputs = T.transaction_inputs
        transaction_outputs = T.transaction_outputs
        print("[ENTER]: run_transaction\n")
        if T.type_of_transaction == 'coins':
            for t_in in transaction_inputs:
                for utxo in self.wallet.utxos.copy():
                    if t_in.transaction_id == utxo.transaction_id and t_in.address == utxo.address \
                    and t_in.amount == utxo.amount:
                        self.wallet.utxos.remove(utxo)
                        break
            for t_out in transaction_outputs:
                if (t_out.amount > 0):
                    self.wallet.utxos.append(t_out)
            fee = T.amount * 0.03
     
        else:
            fee = len(T.message)
        for key, val in self.ring.items():
            if val[0] == validator:
                validator_address = key
            else:
                print("Error: validator_id not in ring")
        fee_tx = Transaction.TransactionIO(T.transaction_id, validator_address, fee)
        self.wallet.utxos.append(fee_tx)
        print("[EXIT]: run_transaction\n")
        return


  
    def run_block(self, B):
        for tx in B.transactions:
            self.run_transaction(tx, B.validator)
            self.transaction_pool.remove(tx)
        self.wallet.utxos_soft = self.wallet.utxos.copy()

  
    #validate and run
    def validate_chain(self, chain):
      genesis_block = chain.blocks[0]
      self.run_block(genesis_block)
      self.chain.add_block(genesis_block)
      
      for block in chain.blocks[1:]:   #exclude genesis block
        if not self.validate_block(block):
          print("[EXIT]: validate_chain: wrong block\n")
          return False
        self.run_block(block)
        self.chain.add_block(block)
      return True


    def stake(self, amount):
      self.create_transaction(0, 'coins', amount)
      return
      

    #public key must be decoded
    def register_node_to_ring(self, public_key, ip):
        #Only bootstrap node brodcasts the ring to all nodes and sends the request node a new id and 1000 BCCs
        if(self.id==0):
            if public_key in self.ring.keys():
                requests.post('http://'+ip+port+'/registerFail', json={'ERROR' : 'Public address already in use!'})
            else:
                self.ring[public_key] = [self.current_id_count, ip, INITIAL_STAKE]
                #maybe error because it was json={'ring' : self.ring}
                self.broadcast(self.ring, "NewNode")
                self.current_id_count+=1
    
                url_newNode = 'http://'+ip+port+'/sendBlockchain'
                blockchain = self.chain.to_dict()
                requests.post(url_newNode, json=blockchain)
    
                self.create_transaction(public_key.encode(), "coins", amount=1000)
  
        return


