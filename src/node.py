import requests
import json
import pickle
import itertools
import time

from copy import deepcopy
from collections import deque
from threading import Lock, Thread

from blockchain import Blockchain
from block import Block, CAPACITY
from wallet import Wallet
from transaction import Transaction
from transaction_input import TransactionInput

# Set default MINING_DIFFICULTY
MINING_DIFFICULTY = 5


class Node:
    """
    A node in the network.

    Attributes:
        id (int): the id of the node.
        nbc (int): the noobcash coins that the node has.
        chain (Blockchain): the blockchain that the node has.
        wallet (Wallet): the wallet of the node.
        ring (list): list of information about other nodes
                     (id, ip, port, public_key, balance).
        lock (Lock): a lock in order to provide mutual exclution in mining.
        stop_mining (boolean): True when mining should stop
                               (when a confirmed block arrives).
        current_block (Block): the block that the node is fills with
                               transactions.
        unconfirmed_blocks (deque): A queue that contains all the blocks
                                    waiting for mining.
    """

    def __init__(self):
        """Inits a Node."""
        self.id = None
        self.nbc = 0
        self.chain = Blockchain()
        self.wallet = Wallet()
        self.ring = []
        self.filter_lock = Lock()
        self.chain_lock = Lock()
        self.block_lock = Lock()
        self.stop_mining = False
        self.current_block = None
        self.unconfirmed_blocks = deque()

    def __str__(self):
        """Returns a string representation of a Node object."""
        return str(self.__class__) + ": " + str(self.__dict__)

    def create_new_block(self):
        """Creates a new block for the blockchain."""
        if len(self.chain.blocks) == 0:
            # Here, the genesis block is created.
            new_idx = 0
            previous_hash = 1
            self.current_block = Block(new_idx, previous_hash)
        else:
            # They will be updated in mining.
            self.current_block = Block(None, None)
        return self.current_block

    def register_node_to_ring(self, id, ip, port, public_key, balance):
        """Registers a new node in the ring.

        This method is called only in the bootstrap node.
        """

        self.ring.append(
            {
                'id': id,
                'ip': ip,
                'port': port,
                'public_key': public_key,
                'balance': balance
            })

    def create_transaction(self, receiver, receiver_id, amount):
        """Creates a new transaction.

        This method creates a new transaction after computing the input that
        the transaction should take.
        """
        # Fill the input of the transaction with UTXOs, by iterating through
        # the previous transactions of the node.
        inputs = []
        inputs_ids = []
        nbc_sent = 0
        for tr in self.wallet.transactions:
            for output in tr.transaction_outputs:
                if (output.recipient == self.wallet.public_key and
                        output.unspent):
                    inputs.append(TransactionInput(tr.transaction_id))
                    inputs_ids.append(tr.transaction_id)
                    output.unspent = False
                    nbc_sent += output.amount
            if nbc_sent >= amount:
                # Exit the loop when UTXOs exceeds the amount of
                # the transaction.
                break

        if nbc_sent < amount:
            # If the node don't have enough coins, the possible inputs turn
            # into unspent again
            for tr in self.wallet.transactions:
                for tr_output in tr.transaction_outputs:
                    if tr_output.transaction_id in inputs_ids:
                        tr_output.unspent = True
            return False

        transaction = Transaction(
            sender_address=self.wallet.public_key,
            sender_id=self.id,
            receiver_address=receiver,
            receiver_id=receiver_id,
            amount=amount,
            transaction_inputs=inputs,
            nbc_sent=nbc_sent
        )

        # Sign the transaction
        transaction.sign_transaction(self.wallet.private_key)

        # Broadcast the transaction to the whole network.
        if not self.broadcast_transaction(transaction):
            for tr in self.wallet.transactions:
                for tr_output in tr.transaction_outputs:
                    if tr_output.transaction_id in inputs_ids:
                        tr_output.unspent = True
            return False

        return True

    def add_transaction_to_block(self, transaction):
        """Add transaction to the block.

        This method adds a transaction in the block and checks if the current
        block is ready to be mined. Also, the wallet transactions and the
        balance of each node are updated.
        """

        # If the node is the recipient or the sender of the transaction,
        # it adds the transaction in its wallet.
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
        if self.current_block is None:
            self.current_block = self.create_new_block()

        self.block_lock.acquire()
        if self.current_block.add_transaction(transaction):

            # Mining procedure includes:
            # - add the current block in the queue of unconfirmed blocks.
            # - wait until the thread gets the lock.
            # - check that the queue is not empty.
            # - mine the first block of the queue.
            # - if mining succeeds, broadcast the mined block.
            # - if mining fails, put the block back in the queue and wait
            #   for the lock.

            # Update previous hash and index in case of insertions in the chain
            self.unconfirmed_blocks.append(deepcopy(self.current_block))
            self.current_block = self.create_new_block()
            self.block_lock.release()
            while True:
                with self.filter_lock:
                    if (self.unconfirmed_blocks):
                        mined_block = self.unconfirmed_blocks.popleft()
                        mining_result = self.mine_block(mined_block)
                        if (mining_result):
                            break
                        else:
                            self.unconfirmed_blocks.appendleft(mined_block)
                    else:
                        return
            self.broadcast_block(mined_block)
        else:
            self.block_lock.release()

    def broadcast_transaction(self, transaction):
        """Broadcasts a transaction to the whole network.

        This is called each time a new transaction is created. In order to
        send the transaction simultaneously, each request is sent by a
        different thread. If all nodes accept the transaction, the node adds
        it in the current block.
        """
        def thread_func(node, responses, endpoint):
            if node['id'] != self.id:
                address = 'http://' + node['ip'] + ':' + node['port']
                response = requests.post(address + endpoint,
                                         data=pickle.dumps(transaction))
                responses.append(response.status_code)

        threads = []
        responses = []
        for node in self.ring:
            thread = Thread(target=thread_func, args=(
                node, responses, '/validate_transaction'))
            threads.append(thread)
            thread.start()

        for tr in threads:
            tr.join()

        for res in responses:
            if res != 200:
                return False
        threads = []
        responses = []
        for node in self.ring:
            thread = Thread(target=thread_func, args=(
                node, responses, '/get_transaction'))
            threads.append(thread)
            thread.start()

        self.add_transaction_to_block(transaction)
        return True

    def validate_transaction(self, transaction):
        """Validates an incoming transaction.

        The validation consists of:
        - verification of the signature.
        - check that the transaction inputs are unspent transactions.
        - create the 2 transaction outputs and add them in UTXOs list.
        """

        if not transaction.verify_signature():
            return False

        for node in self.ring:
            if node['public_key'] == transaction.sender_address:
                if node['balance'] >= transaction.amount:
                    return True
        return False

    def mine_block(self, block):
        """Implements the proof-of-work.

        This methods implements the proof of work algorithm.
        """

        block.nonce = 0
        block.index = self.chain.blocks[-1].index + 1
        block.previous_hash = self.chain.blocks[-1].current_hash
        computed_hash = block.get_hash()
        while (not computed_hash.startswith('0' * MINING_DIFFICULTY) and
                not self.stop_mining):
            block.nonce += 1
            computed_hash = block.get_hash()
        block.current_hash = computed_hash

        return not self.stop_mining

    def broadcast_block(self, block):
        """
        Broadcasts a validated block in the whole network.

        This method is called each time a new block is mined. If at least
        one node accepts the block, the node adds the block in the chain.
        """

        block_accepted = False

        def thread_func(node, responses):
            if node['id'] != self.id:
                address = 'http://' + node['ip'] + ':' + node['port']
                response = requests.post(address + '/get_block',
                                         data=pickle.dumps(block))
                responses.append(response.status_code)

        threads = []
        responses = []
        for node in self.ring:
            thread = Thread(target=thread_func, args=(
                node, responses))
            threads.append(thread)
            thread.start()

        for tr in threads:
            tr.join()

        for res in responses:
            if res == 200:
                block_accepted = True

        if block_accepted:
            with self.chain_lock:
                if self.validate_block(block):
                    self.chain.blocks.append(block)

    def validate_previous_hash(self, block):
        """Validates the previous hash of an incoming block.

        The previous hash must be equal to the hash of the previous block in
        the blockchain.
        """

        return block.previous_hash == self.chain.blocks[-1].current_hash

    def validate_block(self, block):
        """Validates an incoming block.

            The validation consists of:
            - check that current hash is valid.
            - validate the previous hash.
        """
        return (self.validate_previous_hash(block) and
                (block.current_hash == block.get_hash()))

    def filter_blocks(self, mined_block):
        """Filters the queue of the unconfirmed blocks.

        This method is called each time a new block is added in the blockchain.
        The incoming block may contains transactions that are included in the
        unconfirmed blocks too. These 'double' transactions are removed from
        the queue.
        """
        with self.block_lock:
            total_transactions = list(itertools.chain.from_iterable(
                [
                    unc_block.transactions
                    for unc_block
                    in self.unconfirmed_blocks
                ]))

            if (self.current_block):
                total_transactions.extend(self.current_block.transactions)

            self.current_block.transactions = []

            filtered_transactions = [
                transaction
                for transaction
                in total_transactions
                if (
                    transaction
                    not in mined_block.transactions
                )
            ]

            final_idx = 0
            if not self.unconfirmed_blocks:
                self.current_block.transactions = deepcopy(
                    filtered_transactions)
                return

            i = 0
            while ((i + 1) * CAPACITY <= len(filtered_transactions)):
                self.unconfirmed_blocks[i].transactions = deepcopy(
                    filtered_transactions[i * CAPACITY:(
                        i + 1) * CAPACITY])
                i += 1

            if i * CAPACITY < len(filtered_transactions):
                self.current_block.transactions = deepcopy(
                    filtered_transactions[i * CAPACITY:])

            for i in range(len(self.unconfirmed_blocks) - i):
                self.unconfirmed_blocks.pop()

        return

    def share_ring(self, ring_node):
        """Shares the node's ring (neighbor nodes) to a specific node.

        This function is called for every newcoming node in the blockchain.
        """

        address = 'http://' + ring_node['ip'] + ':' + ring_node['port']
        requests.post(address + '/get_ring',
                      data=pickle.dumps(self.ring))

    def validate_chain(self, chain):
        """Validates all the blocks of a chain.

        This function is called every time a node receives a chain after
        a conflict.
        """
        blocks = chain.blocks
        for i in range(len(blocks)):
            if i == 0:
                if (blocks[i].previous_hash != 1 or
                        blocks[i].current_hash != blocks[i].get_hash()):
                    return False
            else:
                valid_current_hash = (
                    blocks[i].current_hash == blocks[i].get_hash()
                )
                valid_previous_hash = (
                    blocks[i].previous_hash == blocks[i - 1].current_hash
                )
                if not valid_current_hash or not valid_previous_hash:
                    return False
        return True

    def share_chain(self, ring_node):
        """Shares the node's current blockchain to a specific node.

        This function is called whenever there is a conflict and the node is
        asked to send its chain by the ring_node.
        """

        address = 'http://' + ring_node['ip'] + ':' + ring_node['port']
        requests.post(address + '/get_chain', data=pickle.dumps(self.chain))

    def resolve_conflicts(self, new_block):
        """Resolves conflicts of multiple blockchains.

        This function is called when a node receives a block for which it
        can't validate its previous hash.

        In order to resolve the conflict:
            - broadcast a request to get the current blockchains
              of the other nodes.
            - validate the given blockchains.
            - keep the longest one.
        """
        def thread_func(node, chains):
            if node['id'] != self.id:
                address = 'http://' + node['ip'] + ':' + node['port']
                response = requests.get(address + "/send_chain")
                new_blockchain = pickle.loads(response._content)
                chains.append(new_blockchain)

        threads = []
        chains = []
        for node in self.ring:
            thread = Thread(target=thread_func, args=(
                node, chains))
            threads.append(thread)
            thread.start()

        for tr in threads:
            tr.join()

        selected_chain = None
        for chain in chains:
            if selected_chain:
                if (self.validate_chain(chain) and
                        (
                            len(chain.blocks) >
                            len(selected_chain.blocks)
                )):
                    selected_chain = chain
            else:
                if (self.validate_chain(chain)
                        and (
                            len(chain.blocks) >
                            len(self.chain.blocks)
                )):
                    selected_chain = chain

        if selected_chain:
            self.stop_mining = True
            with self.filter_lock:
                i = len(selected_chain.blocks) - 1
                while (
                        i > 0 and
                        ((
                            selected_chain.blocks[i].current_hash !=
                            self.chain.blocks[-1].current_hash
                        ))):
                    i -= 1

                for bl in reversed(self.chain.blocks[i + 1:]):
                    self.unconfirmed_blocks.appendleft(bl)

                for bl in selected_chain.blocks[i + 1:]:
                    self.filter_blocks(bl)

                self.chain = selected_chain
                self.stop_mining = False
        return self.validate_block(new_block)
