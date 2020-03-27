import requests
import pickle
import time

from flask import Blueprint, jsonify, request, render_template

from node import Node
from block import Block
from transaction import Transaction
from transaction_output import TransactionOutput
from node import Node

###########################################################
################## INITIALIZATIONS ########################
###########################################################


# Define the node object of the current node.
node = Node()
# Define the number of nodes in the network.
n = 0
# Define a Blueprint for the api endpoints.
rest_api = Blueprint('rest_api', __name__)


###########################################################
################## API/API COMMUNICATION ##################
###########################################################


@rest_api.route('/get_block', methods=['POST'])
def get_block():
    '''Endpoint that gets an incoming block, validates it and adds it in the
        blockchain.

        Input:
            new_block: the incoming block in pickle format.
        Returns:
            message: the outcome of the procedure.
    '''
    new_block = pickle.loads(request.get_data())
    node.chain_lock.acquire()
    if node.validate_block(new_block):
        # If the block is valid:
        # - Add block to the current blockchain.
        # - Remove the new_block's transactions from the unconfirmed_blocks of the node.
        # Update previous hash and index in case of insertions in the chain
        node.stop_mining = True
        with node.filter_lock:
            node.chain.blocks.append(new_block)
            node.chain_lock.release()
            node.filter_blocks(new_block)
            node.stop_mining = False
    else:
        # If the block is not valid, check if the signature is not authentic or
        # there is a conflict.
        if node.validate_previous_hash(new_block):
            node.chain_lock.release()
            return jsonify({'message': "The signature is not authentic. The block has been modified."}), 401
        else:
            # Resolve conflict (multiple blockchains/branch).
            if node.resolve_conflicts(new_block):
                # Add block to the current blockchain
                node.stop_mining = True
                with node.filter_lock:
                    node.chain.blocks.append(new_block)
                    node.chain_lock.release()
                    # Remove the new_block's transactions from the unconfirmed_blocks of the node.
                    node.filter_blocks(new_block)
                    node.stop_mining = False
            else:
                node.chain_lock.release()
                return jsonify({'mesage': "Block rejected."}), 409

    return jsonify({'message': "OK"})


@rest_api.route('/validate_transaction', methods=['POST'])
def validate_transaction():
    '''Endpoint that gets an incoming transaction and valdiates it.

        Input:
            new_transaction: the incoming transaction in pickle format.
        Returns:
            message: the outcome of the procedure.
    '''
    new_transaction = pickle.loads(request.get_data())
    if node.validate_transaction(new_transaction):
        return jsonify({'message': "OK"}), 200
    else:
        return jsonify({'message': "The signature is not authentic"}), 401


@rest_api.route('/get_transaction', methods=['POST'])
def get_transaction():
    '''Endpoint that gets an incoming transaction and adds it in the
        block.

        Input:
            new_transaction: the incoming transaction in pickle format.
        Returns:
            message: the outcome of the procedure.
    '''

    new_transaction = pickle.loads(request.get_data())
    node.add_transaction_to_block(new_transaction)

    return jsonify({'message': "OK"}), 200


@rest_api.route('/register_node', methods=['POST'])
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

    # Get the arguments
    node_key = request.form.get('public_key')
    node_ip = request.form.get('ip')
    node_port = request.form.get('port')
    node_id = len(node.ring)

    # Add node in the list of registered nodes.
    node.register_node_to_ring(
        id=node_id, ip=node_ip, port=node_port, public_key=node_key, balance=0)

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
                    receiver_id=ring_node['id'],
                    amount=100
                )

    return jsonify({'id': node_id})


@rest_api.route('/get_ring', methods=['POST'])
def get_ring():
    '''Endpoint that gets a ring (information about other nodes).

        Input:
            ring: the ring in pickle format.
        Returns:
            message: the outcome of the procedure.
    '''
    node.ring = pickle.loads(request.get_data())
    # Update the id of the node based on the given ring.
    for ring_node in node.ring:
        if ring_node['public_key'] == node.wallet.public_key:
            node.id = ring_node['id']
    return jsonify({'message': "OK"})


@rest_api.route('/get_chain', methods=['POST'])
def get_chain():
    '''Endpoint that gets a blockchain.

        Input:
            chain: the blockchain in pickle format.
        Returns:
            message: the outcome of the procedure.
    '''
    node.chain = pickle.loads(request.get_data())
    return jsonify({'message': "OK"})


@rest_api.route('/send_chain', methods=['GET'])
def send_chain():
    '''Endpoint that sends a blockchain.

        Returns:
            the blockchain of the node in pickle format.
    '''
    return pickle.dumps(node.chain)


##############################################################
################## CLIENT/API COMMUNICATION ##################
##############################################################


@rest_api.route('/api/create_transaction', methods=['POST'])
def create_transaction():
    '''Endpoint that creates a new transaction.

        Input:
            receiver: the id of the receiver node.
            amount: the amount of NBCs to send.
        Returns:
            message: the outcome of the procedure.
    '''

    # Get the arguments.
    receiver_id = int(request.form.get('receiver'))
    amount = int(request.form.get('amount'))

    # Find the address of the receiver.
    receiver_public_key = None
    for ring_node in node.ring:
        if (ring_node['id'] == receiver_id):
            receiver_public_key = ring_node['public_key']
    if (receiver_public_key and receiver_id != node.id):
        if node.create_transaction(receiver_public_key, receiver_id, amount):
            return jsonify({'message': 'The transaction was successful.', 'balance': node.wallet.get_balance()}), 200
        else:
            return jsonify({'message': 'Not enough NBCs.', 'balance':node.wallet.get_balance()}), 400
    else:
        return jsonify({'message': 'Transaction failed. Wrong receiver id.'}), 400


@rest_api.route('/api/get_balance', methods=['GET'])
def get_balance():
    '''Endpoint that returns the current balance of the node.

        Returns:
            message: the current balance.
    '''
    return jsonify({'message': 'Current balance: ' + str(node.wallet.get_balance()) + ' NBCs'})


@rest_api.route('/api/get_transactions', methods=['GET'])
def get_transactions():
    '''Endpoint that returns the transactions of the last confirmed block.

        Returns:
            a formatted list of transactions in pickle format.
    '''
    return pickle.dumps([tr.to_list() for tr in node.chain.blocks[-1].transactions])


@rest_api.route('/api/get_my_transactions', methods=['GET'])
def get_my_transactions():
    '''Endpoint that returns all the transactions of a node (as a sender of receiver).

        Returns:
            a formatted list of transactions in pickle format.
    '''
    return pickle.dumps([tr.to_list() for tr in node.wallet.transactions])


@rest_api.route('/api/get_id', methods=['GET'])
def get_id():
    '''Endpoint that returns the id of the node.

        Returns:
            message: the id of the node.
    '''
    return jsonify({'message': node.id})


@rest_api.route('/api/get_block_time', methods=['GET'])
def get_block_time():
    '''Endpoint that returns the block_time.

        Returns:
            message: the mean value of the block times.
    '''
    return jsonify({'message': 'Block time: ' + str(sum(node.block_times) / len(node.block_times)) + ' in ' + str(len(node.chain.blocks))})
