import requests
from argparse import ArgumentParser
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


import block
import node
import blockchain
import wallet
import transaction
import wallet

# All nodes are aware of the ip and the port of the bootstrap
# node, in order to communicate with it when entering the network.
BOOTSTRAP_IP = '127.0.0.1'
BOOTSTRAP_PORT = '5000'

# Capacity defines the maximum number of transactions
# a block can have.
CAPACITY = 10

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
blockchain = Blockchain()

'''

# get all transactions in the blockchain
@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200

'''

if __name__ == '__main__':
    parser = ArgumentParser(description='Rest backend of noobcash')
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    parser.add_argument('-bootstrap', default=False,
                        action='store_true', help='')

    args = parser.parse_args()
    port = args.port
    is_bootstrap = args.bootstrap

    if (is_bootstrap):

        #app.run(host='127.0.0.1', port=port)
