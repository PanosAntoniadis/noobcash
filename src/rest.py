import requests
from argparse import ArgumentParser
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from block import Block
from node import Node
from transaction import Transaction

# All nodes are aware of the ip and the port of the bootstrap
# node, in order to communicate with it when entering the network.
BOOTSTRAP_IP = '127.0.0.1'
BOOTSTRAP_PORT = '5000'

# Capacity defines the maximum number of transactions
# a block can have.
CAPACITY = 10

# Define the difficulty of proof-of-work.
MINING_DIFFICULTY = 4

app = Flask(__name__)
#app.config["DEBUG"] = True
CORS(app)

# Initialize a node.
node = None


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
    node_id = len(node.ring) + 1

    # Add node in the list of registered nodes.
    node.register_node_to_ring(
        id=node_id, ip=node_ip, port=node_port, public_key=node_key)

    node.create_transaction(
        receiver=node_key, amount=100)

    return jsonify({'id': node_id})


if __name__ == '__main__':
    # Define the argument parser.
    parser = ArgumentParser(description='Rest api of noobcash.')
    parser.add_argument('-p', default=5000,
                        type=int, help='port to listen on')
    parser.add_argument(
        '-n', type=int, help='number of nodes in the blockchain')
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

        # Defines the genesis block.
        gen_block = node.create_new_block(nonce=0, previous_hash=1)

        # Adds the first and only transaction in the genesis block.
        first_transaction = Transaction(
            sender_address=0, receiver_address=node.wallet.public_key, amount=100 * n, transaction_inputs=None, nbc_sent=100 * n)
        gen_block.add_transaction(first_transaction)

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
        # be different here.

        response = requests.post(
            register_address,
            data={'public_key': node.wallet.public_key,
                  'ip': BOOTSTRAP_IP, 'port': port}
        )

        if response.status_code == 200:
            print(response.json()['id'])

        node.id = response.json()['id']

        # Listen in the specified address (ip:port)
        app.run(host=BOOTSTRAP_IP, port=port)
