import os
import requests
import socket
import pickle
import sys
import time

from argparse import ArgumentParser
from texttable import Texttable

# Add config file in our path.
sys.path.insert(0, '../src')
import config

# Get the IP address of the device
if config.LOCAL:
    IPAddr = '127.0.0.1'
else:
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

total_time = 0
num_transactions = 0

def start_transactions():
    """This function sends the transactions of the text file"""

    global total_time
    global num_transactions
    address = 'http://' + IPAddr + ':' + str(port) + '/api/create_transaction'
    with open(input_file, 'r') as f:
        for line in f:
            # Get the info of the transaction.
            line = line.split()
            receiver_id = int(line[0][2])
            amount = int(line[1])
            transaction = {'receiver': receiver_id, 'amount': amount}

            print('\nSending %d nbc coins to the node with id %d ...' %
                  (amount, receiver_id))

            # Send the current transaction.
            try:
                start_time = time.time()
                response = requests.post(address, data=transaction)
                end_time = time.time() - start_time
                message = response.json()["message"]
                if response.status_code == 200:
                    total_time += end_time
                    num_transactions += 1
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
            transactions.append(['receive', tr[2], tr[0], "Me"])
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
        response = requests.get(address).json()
        message = response['message']
        balance = str(response['balance'])
        print('\n' + message + ' ' + balance + '\n')
        print("The balance calculated based on the transactions\nin the table above is: " +
              str(balance) + " NBCs\n")
    except:
        exit("\nSomething went wrong while receiving your balance.\n")

    try:
        address = 'http://' + IPAddr + ':' + str(port) + '/api/get_metrics'
        response = requests.get(address).json()
        num_blocks = response['num_blocks'] - 1
        capacity = response['capacity']
        difficulty = response['difficulty']
        with open('./results', 'a') as f:
            f.write('Total transactions: %d\n' %num_transactions)
            f.write('Total blocks (without genesis): %d\n' %num_blocks)
            f.write('Total time: %f\n' %total_time)
            f.write('Capacity: %d\n' %capacity)
            f.write('Difficulty: %d\n' %difficulty)
            f.write('\n')
    except:
        exit("\nSomething went wrong while receiving the total blocks.\n")

def get_id():
    address = 'http://' + IPAddr + ':' + str(port) + '/api/get_id'
    response = requests.get(address).json()
    message = response['message']
    return message


if __name__ == "__main__":
    # Define the argument parser.
    parser = ArgumentParser(
        description='Sends transactions in the noobcash blockchain given from a text file.')

    required = parser.add_argument_group('required arguments')

    required.add_argument(
        '-input', help='Path to the directory of the transactions. Each text file contains one transaction per line in\nthe following format: id[#] amount, e.g. id3 10', required=True)

    required.add_argument(
        '-p', type=int, help='Port that the api is listening on', required=True)

    # Parse the given arguments.
    args = parser.parse_args()
    input_dir = args.input
    port = args.p

    input("\n Press Enter to start the transactions...\n")

    # Find the corresponding transaction file.
    id = get_id()
    input_file = os.path.join(input_dir, 'transactions' + str(id) + '.txt')

    print('Reading %s ...' % input_file)

    start_transactions()
