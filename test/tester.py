import config
import os
import requests
import socket
import pickle
import sys

from argparse import ArgumentParser
from texttable import Texttable

sys.path.insert(0, '../src')

# Get the IP address of the device
if config.LOCAL:
    IPAddr = '127.0.0.1'
else:
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)


def start_transactions():
    address = 'http://' + IPAddr + ':' + str(port) + '/api/create_transaction'
    with open(input_file, 'r') as f:
        for line in f:
            line = line.split()
            receiver_id = int(line[0][2])
            amount = int(line[1])
            transaction = {'receiver': receiver_id, 'amount': amount}
            print('\nSending %d nbc coins to the node with id %d ...' %
                  (amount, receiver_id))

            try:
                response = requests.post(address, data=transaction).json()
                message = response["message"]
                print("\n" + message + '\n')
            except:
                exit("\nNode is not active. Try again later.\n")

    input("\nWhen all transactions in the network are over, press Enter to get the final balance ...\n")

    try:
        address = 'http://' + IPAddr + ':' + \
            str(port) + '/api/get_my_transactions'
        response = requests.get(address)
        data = pickle.loads(response._content)
    except:
        exit("\nSomething went wrong while receiving your transactions.\n")

    transactions = []
    balance = 0
    for tr in data:
        if tr[0] == id:
            transactions.append(['send', tr[2], "Me", tr[1]])
            balance -= int(tr[2])
        elif tr[1] == id:
            transactions.append(['receive', tr[2], tr[1], "Me"])
            balance += int(tr[2])
        else:
            exit('Wrong transactions!')

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t',  # text
                          't',  # text
                          't',  # text
                          't'])  # text
    table.set_cols_align(["c", "c", "c", "c"])
    headers = ["Type", "Amount", "From", "To"]
    rows = []
    rows.append(headers)
    rows.extend(transactions)
    table.add_rows(rows)
    print(table.draw() + "\n")

    try:
        address = 'http://' + IPAddr + ':' + str(port) + '/api/get_balance'
        # Use the address below for deployment
        #address = 'http://' + IPAddr + ':'+ str(PORT) +'/api/get_balance'
        response = requests.get(address).json()
        message = response['message']
        print('\n' + message + '\n')
        print("The balance calculated based on the transactions\nin the table above is: " +
              str(balance) + " NBCs\n")
    except:
        exit("\nSomething went wrong while receiving your balance.\n")


def get_id():
    address = 'http://' + IPAddr + ':' + str(port) + '/api/get_id'
    response = requests.get(address).json()
    message = response['message']
    return message


if __name__ == "__main__":
    # Define the argument parser.
    parser = ArgumentParser(
        description='Sends transactions in the noobcash blockchain given a text file.')
    parser.add_argument(
        '-input', help='Path to the directory of the transactions. Each text file contains one transaction per line in\nthe following format: id[#] amount, e.g. id3 10', required=True)

    parser.add_argument(
        '-p', type=int, help='port that the api is listening on', required=True)

    # Parse the given arguments.
    args = parser.parse_args()
    input_dir = args.input
    port = args.p

    input("\nPress Enter to start the transactions...\n")

    id = get_id()
    input_file = os.path.join(input_dir, 'transactions' + str(id) + '.txt')

    print('Reading %s ...' % input_file)

    start_transactions()
