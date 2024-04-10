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
  response = requests.post(url, json={'amount' : float(amount)})
  print('Stake updated to: ', response.text)
  return amount

def view_block():
  url = 'http://' + IP + PORT + '/view_block'
  response = requests.get(url)
  return response

#gia na elegxoume an theloume coins h message 
def is_number(s):
  try:
      float(s)
      return True
  except ValueError:
      return False

def send_transaction(receiver_address, content):
  url = 'http://' + IP + PORT + '/newTransaction'
  json = {'receiver_address' : receiver_address, 'content' : content}
  json['type_of_transaction'] = 'coins' if is_number(content) else 'message'
  return requests.post(url, json).text
  
if __name__ == '__main__':
  
  def signal_handler(sig, frame):
    print("Forced Termination")
    # exiting python, 0 means "successful termination"
    sys.exit(0)

  print("")
  print("Welcome! Please enter your command or use help to see the available commands.")


  while (1):
    action = input()
    print("\n")
    if(action == 'balance'):
        balance()

    elif(action == 'stake'):
        inputs = action.split()
        if(len(inputs) > 2):
          print("Too many arguments")
        update_stake(float(inputs[1]))

    elif(action == 'view'):
        print(view_block())

    elif(action[0] == 't'):
        inputs = action.split()
        id = inputs[1] 
        amount = inputs[2]
        print(send_transaction(id, amount))

    elif(action == 'exit'):
        print('Exiting...')
        sys.exit(0)

    elif(action == 'help'):
        help_str='''
  HELP\n
  Available commands:\n
  1. t <recipient_address> <amount> \n
  \t--New transaction: send to recipient_address the amount of BBC coins specified by amount.\n
  2. t <recipient_address> <message>
  \t--New transaction: send to recipient_address wallet the message speficied.\n
  3. stake <amount>
  \t--Stake: update the stake of the wallet to the amount specified.
  4. view\n
  \t--View transactions and validator in the last validated block.\n
  5. balance\n
  \t--Show balance: print the balance of the wallet.\n
  6. exit\n
  \t--Exit the program.\n
  '''
        print(help_str)

    else:
        print('Invalid command! Use help to see the available commands')

  pass
