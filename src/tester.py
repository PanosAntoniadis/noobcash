import os
import requests
import socket
import pickle

from argparse import ArgumentParser
from texttable import Texttable

# Getting the IP address of the device
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

# For development (to be removed)
IP = "127.0.0.1"

if __name__ == "__main__":
    # Define the argument parser.
    parser = ArgumentParser(
        description='Sends transactions in the noobcash blockchain given in a text file.')
    parser.add_argument(
        '-input', help='text file that contains one transaction per line', required=True)

    parser.add_argument(
        '-p', type=int, help='port that the api is listen on', required=True)

    # Parse the given arguments.
    args = parser.parse_args()
    input_file = args.input
    port = args.p

    if not os.path.exists(input_file):
        exit('Wrong input file!')

    address = 'http://' + IP + ':' + str(port) + '/api/create_transaction'
    id = int(input_file.split('/')[-1].rstrip('.txt')[-1])

    input("Press Enter to start reading...")

    with open(input_file, 'r') as f:
        for line in f:
            line = line.split()
            receiver_id = int(line[0][2])
            amount = int(line[1])
            transaction = {'receiver': receiver_id, 'amount': amount}
            print('\nSending %d nbc coins in the node with id %d ...' %
                  (amount, receiver_id))

            try:
                response = requests.post(address, data=transaction).json()
                message = response["message"]
                print("\n" + message + '\n')
            except:
                exit("\nNode is not active. Try again later.\n")

    address = 'http://' + IP + ':' + \
        str(port) + '/api/get_my_transactions'
    response = requests.get(address)
    data = pickle.loads(response._content)

    transactions = []
    for tr in data:
        if tr[0] == id:
            transactions.append(['send', tr[2]])
        elif tr[1] == id:
            transactions.append(['receive', tr[2]])
        else:
            exit('Wrong transactions!')

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t',  # text
                          't'])  # text
    table.set_cols_align(["c", "c"])
    headers = ["Type", "Amount"]
    rows = []
    rows.append(headers)
    rows.extend(transactions)
    table.add_rows(rows)
    print(table.draw() + "\n")

    address = 'http://' + IP + ':' + str(port) + '/api/get_balance'
    # Use the address below for deployment
    #address = 'http://' + IPAddr + ':'+ str(PORT) +'/api/get_balance'
    response = requests.get(address).json()
    message = response['message']
    print('\n' + message + '\n')
