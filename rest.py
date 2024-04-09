import requests
from flask import Flask, jsonify, request, render_template
import json
# from flask_cors import CORS
import base64

from argparse import ArgumentParser  

import Node
import Blockchain
import Transaction
import Wallet
import Block
import termcolor as co
import jsonpickle

### JUST A BASIC EXAMPLE OF A REST API WITH FLASK

BOOTSTRAP_URL = 'http://' + Node.BOOTSTRAP_IP + Node.PORT
#master_url='http://192.168.1.1:5000'

app = Flask(__name__)

#change data to tx
def decode_transaction(data):
  
  sender_address = bytes(data['sender_address'], 'utf-8')
  receiver_address = bytes(data['receiver_address'], 'utf-8')
  nonce = data['nonce']
  transaction_inputs = [Transaction.TransactionIO(input[0], bytes(input[1],'utf-8'), float(input[2])) for input in data['transaction_inputs']]
  type_of_transaction = data['type_of_transaction']
  amount = data['amount']
  message = data['message']
  signature = base64.b64decode(data['signature'].encode())

  return Transaction.Transaction(sender_address, receiver_address, nonce, transaction_inputs, type_of_transaction, amount, message, signature)



def decode_block(data):
    index = data['index']
    timestamp = data['timestamp']
    transactions = data['transactions']
    t_list = []
    for t in transactions:
      t_list.append(decode_transaction(t))
    validator = data['validator']
    prev_hash = data['previous_hash']
    
    return Block.Block(index, timestamp, t_list, validator, prev_hash)
    


@app.route('/getBalance', methods=['GET', 'POST'])
def getBalance():
    balance = myNode.wallet.get_balance()
    print(balance)
    return str(balance)


@app.route('/sendTransaction', methods=['POST'])
def receive_transaction():
    data = json.loads((request.data).decode())
    tx = decode_transaction(data)

    
    if((tx.sender_address.decode() not in myNode.nonces \
       or myNode.nonces[tx.sender_address.decode()] < tx.nonce)\
      and myNode.validate_transaction(tx)):
      myNode.add_transaction_to_pool(tx)
      myNode.run_transaction_soft(tx)
  
    if len(myNode.transaction_pool) >= Node.CAPACITY:
      myNode.mint_block(myNode.chain.get_last_block().hash()) 
  
    return 'ok' 



@app.route('/sendBlock', methods=['POST'])
def receive_block():
    data = json.loads((request.data).decode())
    block = decode_block(data)

    if(myNode.validate_block(block)):
      myNode.chain.add_block(block)
    return 'ok'


@app.route('/sendBlockchain', methods=['POST'])
def receiveBlockchain():
    data = json.loads((request.data).decode())

    blocks = data['blocks']

    block_list = []
    for block in blocks:
        block_list.append(decode_block(block))
      
    chain = Blockchain.Blockchain()
    chain.blocks = block_list.copy()
  
    print("I got the Blockchain")
    # print("My BlockChain length is: ", len(myNode.chain.blocks))
    # print("Running BlockChain from the start...")
    myNode.validate_chain(chain)

    return 'ok'



@app.route('/sendNewNode', methods=['POST'])
def addNode():
    data = request.json
    myNode.ring = data.copy()
    #sets self.id as the corresponding id 
    for pub_key, value in myNode.ring.items():
      myNode.stakes_soft[pub_key] = myNode.ring[pub_key][2]
      if(myNode.wallet.public_key.decode() == pub_key):
        myNode.id = value[0]
      
    print("Bootstrap sent the ring to me, my id is", myNode.id)
    print("Ring is:", myNode.ring)
    return 'ok' #??



@app.route('/register', methods=['POST'])
def registerNode():
    data = json.loads((request.data).decode())
    public_key = data['public_key']   #public key is already decoded here
    ip=request.remote_addr
    # print(ip)
  
    print("Received register request from", public_key)
    myNode.register_node_to_ring(public_key,ip)
  
    return 'ok'


@app.route('/registerFail', methods=['POST'])
def renew_pk():
    myNode.wallet = myNode.generate_wallet()
    requests.post(BOOTSTRAP_URL, json={'public_key': myNode.wallet.public_key.decode()})

    return 'ok'



#bootstrap
if __name__ == '__main__':  

  parser = ArgumentParser()
  parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
  args = parser.parse_args()
  port = args.port

  myNode = Node.Node(bootstrap=True, N=5)
  # print(myNode.wallet.public_key)

  app.run(host='192.168.1.1', port=port)


#new node
if __name__ == '__main__':  


  
  parser = ArgumentParser()
  parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
  args = parser.parse_args()
  port = args.port
  
  myNode = Node.Node()
  # print(myNode.wallet.public_key)

  app.run(host='192.168.1.2', port=port)
