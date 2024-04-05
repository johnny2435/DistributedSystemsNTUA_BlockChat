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


master_url='http://192.168.1.1:5000'

app = Flask(__name__)

def decode_transaction(data):
  data = json.loads((request.data).decode())
  
  sender_address = bytes(data['sender_address'], 'utf-8')
  receiver_address = bytes(data['receiver_address'], 'utf-8')
  nonce = data['nonce']
  transaction_inputs = [Transaction.TransactionIO(input[0], bytes(input[1],'utf-8'), int(input[2])) for input in data['transaction_inputs']]
  type_of_transaction = data['type_of_transaction']
  amount = data['amount']
  message = data['message']
  signature = base64.b64decode(data['signature'].encode())

  tx = Transaction.Transaction(sender_address, receiver_address, nonce, transaction_inputs, type_of_transaction, amount, message, signature)
  return tx
  


@app.route('/getBalance', methods=['GET', 'POST'])
def getBalance():
    balance = myNode.wallet.get_balance()
    print(balance)
    return str(balance)




@app.route('/sendTransaction', methods=['POST'])
def receive_transactions():
    data = json.loads((request.data).decode())
    tx = decode_transaction(data)
  
    if(myNode.validate_transaction(tx)):
      myNode.add_transaction_to_pool(tx)
  
    if len(myNode.transaction_pool) >= Node.CAPACITY:
      myNode.mint_block(myNode.chain.get_last_block().hash()) 
  
    return data  #why do they return data





@app.route('/sendNewNode', methods=['POST'])
def addNode():
    data = request.json
    myNode.ring = data.copy()
    #sets self.id as the corresponding id 
    for pub_key, value in data.items():
        if(myNode.wallet.public_key.decode() == pub_key):
            myNode.id = value[0]
            value[2] = Node.INITIAL_STAKE #einai swsto?
    return 'broadcast' #??



if __name__ == '__main__':
  

  parser = ArgumentParser()
  parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
  args = parser.parse_args()
  port = args.port

  myNode = Node.Node()
  # print(myNode.wallet.public_key)

  # myBlock = myNode.create_new_block()

  app.run(host='192.168.1.1', port=port)
