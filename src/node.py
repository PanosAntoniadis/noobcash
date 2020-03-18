import requests
import json
import pickle
import itertools

from copy import deepcopy
from collections import deque
from threading import Lock

from blockchain import Blockchain
from block import Block, CAPACITY
from wallet import Wallet
from transaction import Transaction
from transaction_input import TransactionInput

# Setting MINING_DIFFICULTY
MINING_DIFFICULTY = 4


class Node:
    """
    A node in the network.

    Attributes:
        id (int): the id of the node.
        chain (Blockchain): the blockchain that the node has.
        nbc (int): the noobcash coins that the node has.
        wallet (Wallet): the wallet of the node.
        ring (list): list of information about other nodes (id, ip, port, public_key, balance).
    """

    def __init__(self):
        self.id = None
        self.nbc = 0
        # Initialize a new chain for the node and create its wallet.
        self.chain = Blockchain()
        self.wallet = Wallet()
        self.ring = []
        self.lock = Lock()
        self.stop_mining = False
        self.current_block = None
        self.unconfirmed_blocks = deque()

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def create_new_block(self):
        # Creates a new block for the blockchain.
        if len(self.chain.blocks) > 0:
            new_idx = self.chain.blocks[-1].index + 1
            previous_hash = self.chain.blocks[-1].current_hash
        else:
            new_idx = 0
            previous_hash = 1

        self.current_block = Block(new_idx, previous_hash)
        return self.current_block

    def register_node_to_ring(self, id, ip, port, public_key, balance):
        # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
        # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
        self.ring.append(
            {'id': id, 'ip': ip, 'port': port, 'public_key': public_key, 'balance': balance})

    def create_transaction(self, receiver, amount):
        """
        Creates a transaction.
        """

        # Fill the input of the transaction with UTXOs, by iterating through
        # the previous transactions of the node.
        inputs = []
        nbc_sent = 0
        for tr in self.wallet.transactions:
            for output in tr.transaction_outputs:
                if output.recipient == self.wallet.public_key and output.unspent:
                    inputs.append(TransactionInput(tr.transaction_id))
                    nbc_sent += output.amount
            if nbc_sent >= amount:
                # Exit the loop when UTXOs exceeds the amount of the transaction.
                break

        if nbc_sent < amount:
            return False

        transaction = Transaction(
            sender_address=self.wallet.public_key, receiver_address=receiver, amount=amount,
            transaction_inputs=inputs, nbc_sent=nbc_sent)

        print('Transaction created:')
        print(transaction)
        # sign the transaction
        transaction.sign_transaction(self.wallet.private_key)
        print('Transaction signed:')
        # Broadcast the transaction to the whole network.
        self.broadcast_transaction(transaction)

    def add_transaction_to_block(self, transaction):
        """
        Add transaction to the block and check if its ready to be mined.
        """
        print('I will add a valid transaction in the block')

        # If the node is the recipient or the sender of the transaction, it adds the
        # transaction in its wallet.
        if (transaction.receiver_address == self.wallet.public_key):
            self.wallet.transactions.append(transaction)
        if (transaction.sender_address == self.wallet.public_key):
            self.wallet.transactions.append(transaction)

        # Update the balance of the recipient and the sender.
        for ring_node in self.ring:
            if ring_node['public_key'] == transaction.sender_address:
                ring_node['balance'] -= transaction.amount
            if ring_node['public_key'] == transaction.receiver_address:
                ring_node['balance'] += transaction.amount

        # If the chain contains only the genesis block, a new block
        # is created. In other cases, the block is created after mining.
        if len(self.chain.blocks) == 1:
            self.current_block = self.create_new_block()

        if self.current_block.add_transaction(transaction):
            print('I have to mine')
            self.unconfirmed_blocks.append(deepcopy(self.current_block))
            self.current_block = self.create_new_block()
            while True:
                with self.lock:
                    print('Got the lock')
                    if (self.unconfirmed_blocks):
                        mined_block = self.unconfirmed_blocks.popleft()
                        mining_result = self.mine_block(mined_block)
                        if (mining_result):
                            print('Mine success!')
                            self.broadcast_block(mined_block)
                        else:
                            print('Mine fail, put back the block')
                            self.unconfirmed_blocks.appendleft(mined_block)
                    else:
                        print('No unconfirmed blocks to mine')
                        return

    def broadcast_transaction(self, transaction):
        """
        Broadcasts a transaction to the whole network.
        """
        print('Broadcast the transaction:')
        for node in self.ring:
            if node['id'] != self.id:
                address = 'http://' + node['ip'] + ':' + node['port']
                response = requests.post(address + '/get_transaction',
                                         data=pickle.dumps(transaction))
                if response.status_code != 200:
                    return

        print('My transaction has been accepted!')
        self.add_transaction_to_block(transaction)
        print('My transactions in wallet:')
        print(self.wallet.transactions)
        print('My ring')
        print(self.ring)

    def validate_transaction(self, transaction):
        """
        Validates an incoming transaction.

            The validation consists of:
            a) Verification of the signature.
            b) Check that the transaction inputs are unspent transactions.
            c) Create the 2 transaction outputs and add them in UTXOs list.
        """

        if not transaction.verify_signature():
            return False

        for node in self.ring:
            if node['public_key'] == transaction.sender_address:
                if node['balance'] >= transaction.amount:
                    return True
        return False

    def mine_block(self, block):
        """
        Implements the proof-of-work.
        """
        print('Mining...')
        block.nonce = 0
        # Update previous hash and index in case of insertions in the chain
        block.previous_hash = self.chain.blocks[-1].current_hash
        block.index = self.chain.blocks[-1].index + 1
        computed_hash = block.get_hash()
        while not computed_hash.startswith('0' * MINING_DIFFICULTY) and not self.stop_mining:
            block.nonce += 1
            computed_hash = block.get_hash()
        block.current_hash = computed_hash
        print('Mine ended')

        return not self.stop_mining

    def broadcast_block(self, block):
        """
        Broadcasts a validated block in the rest nodes.
        """
        block_accepted = False
        print('Broadcast the mined block')
        print(self.ring)
        print(self.id)
        for node in self.ring:
            if node['id'] != self.id:
                address = 'http://' + node['ip'] + ':' + node['port']
                response = requests.post(address + '/get_block',
                                         data=pickle.dumps(block))
                if response.status_code == 200:
                    block_accepted = True

        if block_accepted:
            print('My block has been accepted')
            # If at least of the nodes accepted the block, the block is valid.
            self.chain.blocks.append(block)

    def validate_previous_hash(self, block):
        """
        Validates the previous hash of an incoming block.

            The previous hash must be equal to the hash of the previous block in the blockchain.
        """

        return block.previous_hash == self.chain.blocks[-1].current_hash

    def validate_block(self, block):
        """
        Validates an incoming block.

            The validation consists of:
            a) Check that current hash is valid.
            b) Validate the previous hash.
        """
        return self.validate_previous_hash(block) and (block.current_hash == block.get_hash())

    def filter_blocks(self, mined_block):
        """
        Removes from the unconfirmed blocks the transactions that are already inside the mined block.
        """
        total_transactions = itertools.chain.from_iterable(
            [unc_block.transactions for unc_block in self.unconfirmed_blocks])
        filtered_transactions = [transaction for transaction in total_transactions if (
            transaction not in mined_block.transactions)]
        final_idx = 0
        for i, unc_block in enumerate(self.unconfirmed_blocks):
            if ((i + 1) * CAPACITY <= len(filtered_transactions)):
                unc_block.transactions = filtered_transactions[i * CAPACITY:(
                    i + 1) * CAPACITY]
            else:
                unc_block.transactions = filtered_transactions[i * CAPACITY:]
                final_idx = i
                break
        for i in range(len(self.unconfirmed_blocks) - final_idx - 1):
            self.unconfirmed_blocks.pop()

        return

    def share_ring(self, ring_node):
        address = 'http://' + ring_node['ip'] + ':' + ring_node['port']
        requests.post(address + '/get_ring',
                      data=pickle.dumps(self.ring))

    def validate_chain(self, chain):
        """
        Validates all the blocks of a chain.

            This function is called for every newcoming node in the blockchain.
        """

        for block in chain.blocks:
            if not self.validate_block(block):
                return False
        return True

    def share_chain(self, ring_node):
        address = 'http://' + ring_node['ip'] + ':' + ring_node['port']
        requests.post(address + '/get_chain', data=pickle.dumps(self.chain))

    def resolve_conflicts(self, new_block):
        """
        Resolves conflicts of multiple blockchains.

            This function is called when a node receives a block for which it can't validate
            its previous hash.

            In order to resolve the conflict:
            a) Broadcast a request to get the current blockchains of the other nodes.
            b) Validate the given blockchains.
            c) Keep the longest one.
        """
        for ring_node in self.ring:
            if ring_node['id'] != self.id:
                address = 'http://' + ring_node['ip'] + ':' + ring_node['port']
                response = requests.get(address + "/send_chain")
                new_blockchain = pickle.loads(response._content)

                if self.validate_chain(new_blockchain) and len(new_blockchain.blocks) > len(self.chain):
                    self.chain = new_blockchain

        return self.validate_block(new_block)
