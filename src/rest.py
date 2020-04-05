import time
import socket
import requests
import threading

import config
import endpoints
import block

from flask_cors import CORS
from argparse import ArgumentParser
from flask import Flask, jsonify, request, render_template

from block import Block
from transaction import Transaction
from endpoints import node, rest_api

# All nodes are aware of the ip and the port of the bootstrap
# node, in order to communicate with it when entering the network.
BOOTSTRAP_IP = config.BOOTSTRAP_IP
BOOTSTRAP_PORT = config.BOOTSTRAP_PORT

# Get the IP address of the device.
if config.LOCAL:
    IPAddr = BOOTSTRAP_IP
else:
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

# Define the flask environment and register the blueprint with the endpoints.
app = Flask(__name__)
app.register_blueprint(rest_api)
CORS(app)


if __name__ == '__main__':
    # Define the argument parser.
    parser = ArgumentParser(description='Rest api of noobcash.')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional_arguments')

    required.add_argument(
        '-p', type=int, help='port to listen on', required=True)
    required.add_argument(
        '-n', type=int, help='number of nodes in the blockchain', required=True)
    required.add_argument('-capacity', type=int,
                        help='capacity of a block', required=True)
    optional.add_argument('-bootstrap', action='store_true',
                        help='set if the current node is the bootstrap')

    # Parse the given arguments.
    args = parser.parse_args()
    port = args.p
    endpoints.n = args.n
    block.CAPACITY = args.capacity
    is_bootstrap = args.bootstrap

    if (is_bootstrap):
        """
        The bootstrap node (id = 0):
            - registers itself in the ring.
            - creates the genesis block.
            - creates the first transaction and adds it in the genesis block.
            - adds the genesis block in the blockchain (no validation).
            - starts listening in the desired port.
        """

        node.id = 0
        node.register_node_to_ring(
            node.id, BOOTSTRAP_IP, BOOTSTRAP_PORT, node.wallet.public_key, 100 * endpoints.n)

        # Defines the genesis block.
        gen_block = node.create_new_block()
        gen_block.nonce = 0

        # Adds the first and only transaction in the genesis block.
        first_transaction = Transaction(
            sender_address="0", sender_id='0', receiver_address=node.wallet.public_key, receiver_id=node.id, amount=100 * endpoints.n, transaction_inputs=None, nbc_sent=100 * endpoints.n)
        gen_block.transactions.append(first_transaction)
        gen_block.current_hash = gen_block.get_hash()
        node.wallet.transactions.append(first_transaction)

        # Add the genesis block in the chain.
        node.chain.blocks.append(gen_block)
        node.current_block = None

        # Listen in the specified address (ip:port)
        app.run(host=BOOTSTRAP_IP, port=BOOTSTRAP_PORT)
    else:
        """
        The rest nodes (id = 1, .., n-1):
            - communicate with the bootstrap node in order to register them.
            - starts listening in the desired port.
        """

        register_address = 'http://' + BOOTSTRAP_IP + \
            ':' + BOOTSTRAP_PORT + '/register_node'

        def thread_function():
            time.sleep(2)
            response = requests.post(
                register_address,
                data={'public_key': node.wallet.public_key,
                      'ip': IPAddr, 'port': port}
            )

            if response.status_code == 200:
                print("Node initialized")

            node.id = response.json()['id']

        req = threading.Thread(target=thread_function, args=())
        req.start()

        # Listen in the specified address (ip:port)
        app.run(host=IPAddr, port=port)
