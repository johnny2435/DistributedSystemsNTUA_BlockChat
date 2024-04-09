import Block
import Blockchain
import time
import Transaction
import Wallet
import threading
import requests
import math
import random
import termcolor as co

INITIAL_STAKE = 10
CAPACITY = 5
PORT = ':5000'
BOOTSTRAP_IP = '192.168.1.1'


class Node:

  def __init__(self, bootstrap=False, N=0):
    self.wallet = self.generate_wallet()
    self.transaction_pool = []
    self.chain = Blockchain.Blockchain()
    self.nonce = 0
    self.minted = False
    self.stakes_soft = {}
    self.nonces = {}  #pk -> last nonce in block
    
    
    if bootstrap:
      self.id = 0
      self.current_id_count = 1  #id for next node
      self.ring = {
          self.wallet.public_key.decode(): [0, BOOTSTRAP_IP, INITIAL_STAKE]
      }  #addr is decoded in ring

      genesis_transaction = Transaction.Transaction(b'0', self.wallet.public_key,\
      self.nonce, [], "coins", amount=1000.0*N, signature=b'bour_gee')
      genesis_block = Block.Block(0, time.time(), [genesis_transaction], None, 1)

      self.run_block(genesis_block)
      self.chain.add_block(genesis_block)

    else:
      self.id = -1
      self.ring = {}
      
    run_trans = threading.Thread(target=self.run_trans_from_txt, daemon=True)
    run_trans.start()

  
  def id_to_address(self, id):
    for key, val in self.ring.items():
      if val[0] == id:
        return key.encode()
    print("Error: id not in ring")
    return


  def run_trans_from_txt(self):

    time.sleep(5)
    pub_key = {'public_key': self.wallet.get_public_key().decode()}
    if self.id != 0:
      requests.post("http://" + BOOTSTRAP_IP + PORT + "/register", json=pub_key)
    time.sleep(20 + random.randint(0,2))
    if self.id==0:
      if len(self.ring) == CAPACITY:
        for public_key, value in self.ring.items():
          if value[0]!=0:
            self.create_transaction(public_key.encode(), "coins", amount=1000.0)
      else:
        print(co.colored("Error: Nodes did not join in time", 'red'))
    time.sleep(10)
    
    project_path = "./"
    f = open(project_path + "5nodes/trans{}.txt".format(self.id), "r")
    #s = " "
    s = f.readline()
    while s != "":
      receiver, message = s.split(" ", 1)
      receiver_id = receiver[2:]

      print("My balance is:", self.wallet.get_balance())
      self.create_transaction(self.id_to_address(int(receiver_id)), "message", message = message)
      time.sleep(0.5)
      s = f.readline()

    f.close()

  
  def running_node2(self):
    
    time.sleep(2)
    pub_key = {'public_key': self.wallet.get_public_key().decode()}
    if self.id != 0:
      requests.post("http://" + BOOTSTRAP_IP + PORT + "/register", json=pub_key)
    time.sleep(5)  ####

    receiver_address = self.id_to_address(0)

    #print("UTXOS: ", self.wallet.utxos)
    #for tx in self.wallet.utxos:
      #tx.print_trans()
    #print("SOFT UTXOS: ", self.wallet.utxos_soft)
    #for tx in self.wallet.utxos_soft:
      #tx.print_trans()

    print("My balance is now", self.wallet.get_balance())
    print("My soft balance is now", self.wallet.get_balance_soft())

    print("Sending 100 BCC to 0")
    self.create_transaction(receiver_address, "coins", amount=100)
    time.sleep(2)
    print("My balance is now", self.wallet.get_balance())
    print("My soft balance is now", self.wallet.get_balance_soft())

    print("Sending 150 BCC to 1")
    self.create_transaction(receiver_address, "coins", amount=150)
    time.sleep(2)
    print("My balance is now", self.wallet.get_balance())
    print("My soft balance is now", self.wallet.get_balance_soft())
  
  
  def running_node(self):

    time.sleep(2)
    pub_key = {'public_key': self.wallet.get_public_key().decode()}
    if self.id != 0:
      requests.post("http://" + BOOTSTRAP_IP + PORT + "/register",
                    json=pub_key)
    time.sleep(5)  ####

    receiver_address = self.id_to_address(0)
    print("UTXOS: ", self.wallet.utxos)
    for tx in self.wallet.utxos:
      tx.print_trans()
    print("SOFT UTXOS: ", self.wallet.utxos_soft)
    for tx in self.wallet.utxos_soft:
      tx.print_trans()

    print("My balance is now", self.wallet.get_balance())
    print("My soft balance is now", self.wallet.get_balance_soft())

    print("Sending 100 BCC to 0")
    self.create_transaction(receiver_address, "coins", amount=100)
    time.sleep(2)
    print("My balance is now", self.wallet.get_balance())
    print("My soft balance is now", self.wallet.get_balance_soft())

    print("Sending 150 BCC to 0")
    self.create_transaction(receiver_address, "coins", amount=150)
    time.sleep(2)
    print("My balance is now", self.wallet.get_balance())
    print("My soft balance is now", self.wallet.get_balance_soft())

    print("Sending 900 BCC to 0")
    self.create_transaction(receiver_address, "coins", amount=900)
    time.sleep(2)
    print("My balance is now", self.wallet.get_balance())
    print("My soft balance is now", self.wallet.get_balance_soft())

    receiver_address = self.id_to_address(2)
    print("Sending 300 BCC to 2")
    self.create_transaction(receiver_address, "coins", amount=300)
    time.sleep(2)
    print("My balance is now", self.wallet.get_balance())
    print("My soft balance is now", self.wallet.get_balance_soft())

  
  #*
  def generate_wallet(self):
    return Wallet.Wallet()

  
  #*
  def create_transaction(self,
                         receiver,
                         type_of_transaction,
                         amount=0.0,
                         message=""):
    transactionInputs = []
    amount=float(amount)

    for tx in self.wallet.utxos_soft:
      if tx.address == self.wallet.public_key:
        transactionInputs.append(tx)

    trans = Transaction.Transaction(self.wallet.public_key, receiver, self.nonce, \
                        transactionInputs, type_of_transaction, amount, message)

    self.sign_transaction(trans)

    self.nonce += 1
    self.broadcast_transaction(trans)
    return trans

  
  #*
  def sign_transaction(self, transaction):
    transaction.sign_transaction(self.wallet.private_key)
    return

  
  #*
  def verify_signature(self, transaction):
    return transaction.verify_signature()

  
  def broadcast(self, obj, type):
    dict = obj.to_dict() if type != 'NewNode' else obj
    print("[Broadcast]: Broadcasting " + type + " ...")
    for value in self.ring.values():
      #dict has items of type: {public_key: [id, ip, stake]}
      ip_bc = value[1]
      url = 'http://' + ip_bc + PORT + '/send' + type
      #print("sending to " + ip_bc + PORT)
      
      requests.post(url, json=dict)

  
  #*
  def broadcast_transaction(self, tx):
    #print("Created transaction:", tx.to_dict())
    self.broadcast(tx, 'Transaction')

  
  #*
  def broadcast_block(self, block):
    self.broadcast(block, 'Block')

  
  #*
  def validate_transaction(self, T):
    if not T.verify_signature():
      print(co.colored("Error: Wrong signature!\n", 'red'))
      #print(T.to_dict())
      #print(co.colored("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", 'red'))
      return False

    if T.sender_address == T.receiver_address:
      print(co.colored("[Transaction]: ERROR: You can't send BCC/messages to yourself", 'red'))
      return False
    inputs = T.transaction_inputs
    outputs = T.transaction_outputs

    if inputs == []:
      print(co.colored("[Validation Failed]: You got no inputs!", 'red'))
      return False

    #print("SOFT UTXOS: ", self.wallet.utxos_soft)
    #for tx in self.wallet.utxos_soft:
      #tx.print_trans()
    for t_in in inputs:
      found = False
      for t_utxo in self.wallet.utxos_soft:
        if t_in.transaction_id == t_utxo.transaction_id and \
        t_in.address == t_utxo.address and t_in.amount == t_utxo.amount:
          found = True
      if not found:
        print(co.colored("\t\t[Validation Failed]: Transaction Input didn't match UTXOs", 'red'))
        print("\t\t\tTransaction that didn't match:")
        t_in.print_trans()
        print(co.colored("Validation Error Message END\n", 'red'))
        return False

    for t_out in outputs:
      if t_out.amount < 0:
        print(co.colored("[ERROR]: UTXO output has negative value", 'red'))
        return False

    total = sum([t_in.amount for t_in in inputs])

    fee = float(T.amount * 0.03 if T.type_of_transaction == 'coins' else len(T.message))
    stake = self.stakes_soft[
        T.sender_address.decode()]  #sender_address is sender public key
    if total - stake < T.amount + fee:
      print(co.colored("[ERROR]: Sender doesn't have enough money", 'red'))
      return False

    return True

  
  #in rest if capacity of pool is exceeded execute mint_block and broadcast block
  def add_transaction_to_pool(
      self, T):  #in rest first validate then add to pool then run soft
    self.transaction_pool.append(T)
    print(co.colored('Transaction added to pool', 'green'))
    #print(T.to_dict())
    return

  
  #*
  def mint_block(self, prevHash):
    index = self.chain.get_last_block().index + 1
    self.validator = self.Proof_of_Stake()
    if self.id == self.validator:
      block = Block.Block(index, time.time(), [], self.id, prevHash)
      for tx in self.transaction_pool[:CAPACITY]:
        block.add_transaction(tx)
      self.broadcast_block(block)
      return block
    self.minted = True  #:p change it to false uwu
    return -1

  
  #in validate_block remove the tx from pool if block valid
  #*
  #called when a block is received
  #if the block is valid, it validates block and runs transaction_soft for each transaction based on global utxos
  #if the block is invalid it changes nothing and returns false
  def validate_block(self, B, new = False):
    if not new:
      if not self.minted:
        self.validator = self.Proof_of_Stake()
      self.minted = False
      print(co.colored("[ENTER]: validate_block\n", "green"))
      if self.validator != B.validator:
        print(co.colored("[EXIT]: validate_block: Wrong validator\n", 'red'))
        return False

    copy_utxos_soft = self.wallet.utxos_soft.copy()
    copy_stakes_soft = self.stakes_soft.copy()

    self.wallet.utxos_soft = self.wallet.utxos.copy()
    self.stakes_soft = {}
    
    for public_key in self.ring:
      self.stakes_soft[public_key] = self.ring[public_key][2]

    for tx in B.transactions:
      if not self.validate_transaction(tx):
        print(co.colored("[EXIT]: validate_block: invalid transaction\n", 'red'))
        self.wallet.utxos_soft = copy_utxos_soft
        self.stakes_soft = copy_stakes_soft
        return False
      self.run_transaction_soft(tx, B.validator)

    if self.chain.get_last_block().hash() != B.previous_hash:
      print(co.colored("[EXIT]: validate_block: prev hash doesn't match\n", 'red'))
      self.wallet.utxos_soft = copy_utxos_soft
      self.stakes_soft = copy_stakes_soft
      return False

    #at this point we know the block is valid
    for tx in B.transactions:
      self.nonces[tx.sender_address.decode()] = tx.nonce

    for tx in B.transactions:
      #print("Looking for transaction", tx.transaction_id.hexdigest(), "\n")
      for i in range(len(self.transaction_pool)):
        #print("In pool:", self.transaction_pool[i].transaction_id.hexdigest(), "\n")
        if self.transaction_pool[i].transaction_id.hexdigest() == tx.transaction_id.hexdigest():
          #print("Found transaction\n")
          self.transaction_pool.pop(i)
          break

    self.wallet.utxos = self.wallet.utxos_soft.copy()
    for public_key in self.ring:
      self.ring[public_key][2] = self.stakes_soft[public_key]

    print(co.colored("[EXIT]: validate_block: valid\n", 'green'))
    return True

  
  #find a way to save stakes (maybe in ring)
  def Proof_of_Stake(self):
    hash = self.chain.get_last_block().hash()
    #print("\nMy hash is", hash, "\n")
    random.seed(hash)
    total_stakes = sum([v[2] for v in self.ring.values()])
    if total_stakes == 0:
      return False

    stake_target = random.uniform(0, total_stakes)
    current = 0
    l = list(self.ring.values())
    l.sort()

    validator = -1
    for node_id, _, stake_amount in l:
      current += stake_amount
      if current >= stake_target:
        validator = node_id
        break
    if validator == -1:
      print(co.colored("Error: Validator not found", 'red'))
    
    return validator

  
  #validator is None when the transaction is not in a block
  def run_transaction_soft(self, T, validator=None):
    
    if T.receiver_address == 0:
      self.stakes_soft[T.sender_address.decode()] = T.amount
      return

    transaction_inputs = T.transaction_inputs
    transaction_outputs = T.transaction_outputs
    #print("[ENTER]: run_transaction\n")
    if T.type_of_transaction == 'coins':
      for t_in in transaction_inputs:
        for utxo in self.wallet.utxos_soft.copy():
          if t_in.transaction_id == utxo.transaction_id and t_in.address == utxo.address \
          and t_in.amount == utxo.amount:
            self.wallet.utxos_soft.remove(utxo)
            break
      for t_out in transaction_outputs:
        if (t_out.amount > 0):
          self.wallet.utxos_soft.append(t_out)
      fee = T.amount * 0.03

    else:
      fee = len(T.message)

    #find validator's public_address
    if validator is not None and T.sender_address != b'0':
      validator_address = self.id_to_address(validator)
      fee_tx = Transaction.TransactionIO(T.transaction_id.hexdigest(),
                                         validator_address, fee)
      self.wallet.utxos_soft.append(fee_tx)

    #print("[EXIT]: run_transaction\n")
    return

  
  #used only in validate_chain
  def run_block(self, B):
    for tx in B.transactions:
      self.run_transaction_soft(tx, B.validator)
    self.wallet.utxos = self.wallet.utxos_soft.copy()
    for tx in B.transactions:
      self.nonces[tx.sender_address.decode()] = tx.nonce
    

  #validate and run
  def validate_chain(self, chain):
    genesis_block = chain.blocks[0]
    self.run_block(genesis_block)

    self.chain.add_block(genesis_block)

    for block in chain.blocks[1:]:  #exclude genesis block
      if not self.validate_block(block, new = True):  #block also runs in validate_block
        print("[EXIT]: validate_chain: wrong block\n")
        return False
      self.chain.add_block(block)
    return True

  
  def stake(self, amount):
    self.create_transaction(0, 'coins', amount)
    return

  
  #public key must be decoded
  def register_node_to_ring(self, public_key, ip):
    #Only bootstrap node brodcasts the ring to all nodes and sends the request node a new id and 1000 BCCs
    if (self.id == 0):
      if public_key in self.ring:
        requests.post('http://' + ip + PORT + '/registerFail',
                      json={'ERROR': 'Public address already in use!'})
      else:
        self.ring[public_key] = [self.current_id_count, ip, INITIAL_STAKE]
        #maybe error because it was json={'ring' : self.ring}
        self.broadcast(self.ring, "NewNode")
        self.current_id_count += 1

        url_newNode = 'http://' + ip + PORT + '/sendBlockchain'
        blockchain = self.chain.to_dict()
        requests.post(url_newNode, json=blockchain)
        

    return
