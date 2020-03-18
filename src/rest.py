import ast
import time
import socket
import pickle
import requests
import threading

from flask_cors import CORS
from argparse import ArgumentParser
from flask import Flask, jsonify, request, render_template

from node import Node
from block import Block
from transaction import Transaction
from transaction_output import TransactionOutput

# All nodes are aware of the ip and the port of the bootstrap
# node, in order to communicate with it when entering the network.
BOOTSTRAP_IP = '127.0.0.1'
BOOTSTRAP_PORT = '5000'


app = Flask(__name__)
# app.config["DEBUG"] = True
CORS(app)

# Getting the IP address of the device
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

# Initialize a node.
node = None
# Number of nodes in the network.
n = 0

###########################################################
################## API/API COMMUNICATION ##################
###########################################################

@app.route('/get_block', methods=['POST'])
def get_block():
    print('Got a new block')
    new_block = pickle.loads(request.get_data())
    print(len(node.chain.blocks))
    if node.validate_block(new_block):
        print('The block is valid')
        # Add block to the current blockchain
        node.chain.blocks.append(new_block)
        node.stop_mining = True
        print('Mining STOP!!')
        with node.lock:
            print('Got the lock')
            # Remove the new_block's transactions from the unconfirmed_blocks of the node
            node.filter_blocks(new_block)
            node.stop_mining = False
            print('Mining START!!')
    else:
        print('The block is not valid')
        if node.validate_previous_hash(new_block):
            return jsonify({'message': "The signature is not authentic. The block has been modified."}), 401
        else:
            print('We have a conflict')
            # Resolve conflict (multiple blockchains/branch)
            if node.resolve_conflicts(new_block):
                # Add block to the current blockchain
                node.chain.blocks.append(new_block)
                node.stop_mining = True
                with node.lock:
                    # Remove the new_block's transactions from the unconfirmed_blocks of the node
                    node.filter_blocks(new_block)
                    node.stop_mining = False
            else:
                return jsonify({'mesage': "Block rejected."}), 409

    return jsonify({'message': "OK"})


@app.route('/get_transaction', methods=['POST'])
def get_transaction():
    print('Got a new transaction')
    new_transaction = pickle.loads(request.get_data())

    if node.validate_transaction(new_transaction):
        print('Transaction is valid')
        node.add_transaction_to_block(new_transaction)
        print('Transaction added:')
        print(new_transaction)
    else:
        return jsonify({'message': "The signature is not authentic"}), 401

    return jsonify({'message': "OK"}), 200


@app.route('/register_node', methods=['POST'])
def register_node():
    '''Endpoint that registers a new node in the network.
        It is called only in the bootstrap node.

        Input:
            public_key: the public key of node to enter.
            ip: the ip of the node to enter.
            port: the port of the node to enter.

        Returns:
            id: the id that the new node is assigned.
    '''

    # Get the argument
    node_key = request.form.get('public_key')
    node_ip = request.form.get('ip')
    node_port = request.form.get('port')
    node_id = len(node.ring)

    # Add node in the list of registered nodes.
    node.register_node_to_ring(
        id=node_id, ip=node_ip, port=node_port, public_key=node_key, balance=0)

    ####### ATTENTION #######
    # When all nodes are registered, the bootstrap node sends them:
    # - the current chain
    # - the ring
    # - the first transaction
    if (node_id == n - 1):
        for ring_node in node.ring:
            if ring_node["id"] != node.id:
                node.share_chain(ring_node)
                node.share_ring(ring_node)
        for ring_node in node.ring:
            if ring_node["id"] != node.id:
                node.create_transaction(
                    receiver=ring_node['public_key'],
                    receiver_id =ring_node['id'],
                    amount=100
                )

    return jsonify({'id': node_id})


@app.route('/get_ring', methods=['POST'])
def get_ring():
    node.ring = pickle.loads(request.get_data())
    # Update the id based on the given ring.
    for ring_node in node.ring:
        if ring_node['public_key'] == node.wallet.public_key:
            node.id = ring_node['id']
    return jsonify({'message': "OK"})


@app.route('/get_chain', methods=['POST'])
def get_chain():
    node.chain = pickle.loads(request.get_data())
    return jsonify({'message': "OK"})


@app.route('/send_chain', methods=['GET'])
def send_chain():
    return pickle.dumps(node.chain)

##############################################################
################## CLIENT/API COMMUNICATION ##################
##############################################################

@app.route('/api/create_transaction', methods=['POST'])
def create_transaction():
    receiver_id = int(request.form.get('receiver'))
    amount = int(request.form.get('amount'))
    receiver_public_key = None

    for ring_node in node.ring:
        if (ring_node['id'] == receiver_id):
            receiver_public_key = ring_node['public_key']
    if (receiver_public_key and receiver_id!=node.id):
        if node.create_transaction(receiver_public_key, receiver_id, amount):
            return jsonify({'message':'The transaction was successful.', 'balance': node.wallet.get_balance()})
        else:
            return jsonify({'message':'Transaction failed. Please try again later.'})
    else:
        return jsonify({'message':'Transaction failed. Wrong receiver id.'})

@app.route('/api/get_balance', methods=['GET'])
def get_balance():
    return jsonify({'message':'Current balance: '+ str(node.wallet.get_balance())+' NBCs'})

@app.route('/api/get_transactions', methods=['GET'])
def get_transactions():
    return pickle.dumps([tr.to_list() for tr in node.chain.blocks[-1].transactions])


if __name__ == '__main__':
    # Define the argument parser.
    parser = ArgumentParser(description='Rest api of noobcash.')
    parser.add_argument('-p', type=int, help='port to listen on', required=True)
    parser.add_argument(
        '-n', type=int, help='number of nodes in the blockchain', required=True)
    parser.add_argument('-bootstrap', action='store_true',
                        help='set if the current node is the bootstrap')

    # Parse the given arguments.
    args = parser.parse_args()
    port = args.p
    n = args.n
    is_bootstrap = args.bootstrap

    # Initialize the node object of the current node.
    node = Node()

    if (is_bootstrap):
        """
        The bootstrap node (id = 0) should create the genesis block.
        """

        node.id = 0
        node.register_node_to_ring(
            node.id, BOOTSTRAP_IP, BOOTSTRAP_PORT, node.wallet.public_key, 100 * n)

        # Defines the genesis block.
        gen_block = node.create_new_block()
        gen_block.nonce = 0

        # Adds the first and only transaction in the genesis block.
        first_transaction = Transaction(
            sender_address="0", sender_id='0', receiver_address=node.wallet.public_key, receiver_id=node.id, amount=100 * n, transaction_inputs=None, nbc_sent=100 * n)
        gen_block.add_transaction(first_transaction)
        gen_block.current_hash = gen_block.get_hash()
        node.wallet.transactions.append(first_transaction)

        # Add the genesis block in the chain.
        node.chain.blocks.append(gen_block)
        node.current_block = None
        # Listen in the specified address (ip:port)
        app.run(host=BOOTSTRAP_IP, port=BOOTSTRAP_PORT)
    else:
        """
        The rest nodes communicate with the bootstrap node.
        """

        register_address = 'http://' + BOOTSTRAP_IP + \
            ':' + BOOTSTRAP_PORT + '/register_node'

        ####### ATTENTION #######
        # When the system run in oceanos the ip will
        # be the IPAddr of the device.

        def thread_function():
            time.sleep(2)
            response = requests.post(
                register_address,
                data={'public_key': node.wallet.public_key,
                      'ip': BOOTSTRAP_IP, 'port': port}
            )

            if response.status_code == 200:
                print("Node initialized")

            node.id = response.json()['id']

        req = threading.Thread(target=thread_function, args=())
        req.start()

        # Listen in the specified address (ip:port)
        app.run(host=BOOTSTRAP_IP, port=port)
