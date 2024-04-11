import socket
import sys
import requests

PORT = ':5000'
IP = socket.gethostbyname(socket.gethostname())

def balance():
  url = 'http://' + IP + PORT + '/getBalance'
  response = requests.get(url)
  print('Your balance is :', response.text)
  return response

def update_stake(amount):
  url = 'http://' + IP + PORT + '/stake'
  response = requests.post(url, json={'amount' : amount})
  print('Stake updated to: ', response.text)
  return amount

def view_block():
  url = 'http://' + IP + PORT + '/viewBlock'
  response = requests.get(url)
  return response.text

#gia na elegxoume an theloume coins h message 
def is_number(s):
  try:
      float(s)
      return True
  except ValueError:
      return False

def send_transaction(receiver_id, content):
  url = 'http://' + IP + PORT + '/newTransaction'
  json = {'receiver_id' : receiver_id, 'content' : content}
  json['type_of_transaction'] = 'coins' if is_number(content) else 'message'
  #return json
  return requests.post(url, json = json).text
  
if __name__ == '__main__':
  
  def signal_handler(sig, frame):
    print("Forced Termination")
    # exiting python, 0 means "successful termination"
    sys.exit(0)

  print("Welcome! Please enter your command or use help to see the available commands.")


  while (1):
    action = input()
    print("\n")
    if(action == 'balance'):
        balance()

    elif(action == 'view'):
        print(view_block())

    elif(action.split()[0] == 't'):
        inputs = action.split()
        id = inputs[1] 
        amount = inputs[2]
        print(send_transaction(id, amount))

    elif(action == 'exit'):
        print('Exiting...')
        sys.exit(0)

    elif(action.split()[0] == 'stake'):
        inputs = action.split()
        if(len(inputs) > 2):
          print("Too many arguments")
        update_stake(inputs[1])

    elif(action == 'help'):
        help_str='''
  Available commands:
  1. t <recipient_address> <amount>
  \t--New transaction: send to recipient_address the amount of BBC coins specified by amount.
  2. t <recipient_address> <message>
  \t--New transaction: send to recipient_address wallet the message speficied.
  3. stake <amount>
  \t--Stake: update the stake of the wallet to the amount specified.
  4. view
  \t--View transactions and validator in the last validated block.
  5. balance
  \t--Show balance: print the balance of the wallet.
  6. exit
  \t--Exit the program.
  '''
        print(help_str)

    else:
        print('Invalid command! Use help to see the available commands')

  pass
