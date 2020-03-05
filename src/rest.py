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


app = Flask(__name__)
CORS(app)
blockchain = Blockchain()


# get all transactions in the blockchain

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200


# run it once fore every node
if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
