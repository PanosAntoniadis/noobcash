import requests
from blockchain import Blockchain
from block import Block
from wallet import Wallet


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

    def __init__(self, id, nbc):
        self.id = id
        self.nbc = nbc
        # Initialize a new chain for the node and create its wallet.
        self.chain = Blockchain()
        self.wallet = Wallet()
        self.ring = []

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def create_new_block(self, index, nonce, previous_hash):
        # Creates a new block for the blockchain.
        return Block(index, nonce, previous_hash)

    def register_node_to_ring(self, id, ip, port, public_key):
        # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
        # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
        self.ring.append(
            {'id': id, 'ip': ip, 'port': port, 'public_key': public_key})

    def create_transaction(self, receiver, amount, signature):
        """
        Creates a transaction.
        """

        # Fill the input of the transaction with UTXOs, by iterating through
        # the previous transactions of the node.
        inputs = []
        nbc_sent = 0
        for tr in this.wallet.transactions:
            for output in tr.transaction_outputs:
                if output.recipient == this.wallet.public_key and output.unspent:
                    inputs.append(TransactionInput(tr.transaction_id))
                    nbc_sent += output.amount
                if nbc_sent >= amount:
                    # Exit the loop when UTXOs exceeds the amount of the transaction.
                    break

        transaction = Transaction(
            sender_address=this.wallet.public_key, receiver_address=receiver, amount=amount,
            transaction_inputs=inputs, signature=signature. nbc_sent)

        # Broadcast the transaction to the whole network.
        self.broadcast_transaction(transaction)

    def broadcast_transaction(self, transaction):
        """
        Broadcasts a transaction to the whole network.
        """

        for node in self.ring:
            address = node['ip'] + node['port']
            requests.get(url=address, params=vars(transaction))

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

        for node in ring:
            if node['public_key'] == transaction.sender_address:
                if node['balance'] >= transaction.amount:
                    node['balance'] -= transaction.amount
                    return True
        return False

    def mine_block(self, block):
        """
        Implements the proof-of-work.
        """
        block.nonce = 0
        computed_hash = block.get_hash()
        while not computed_hash.startswith('0' * MINING_DIFFICULTY):
            block.nonce += 1
            computed_hash = block.get_hash()
        return computed_hash

    def broadcast_block(self, block):
        """
        Broadcasts a validated block in the rest nodes.
        """

        for node in self.ring:
            address = node['ip'] + node['port']
            requests.get(url=address, params=vars(block))

    def validate_block(self, block):
        """
        Validates an incoming block.

            The validation consists of:
            a) Check that current hash is valid.
            b) Check that the previous hash equals to the hash of the previous block.
        """

        valid_previous = block.previous_hash == node.chain.blocks[-1].current_hash
        return valid_previous and (block.current_hash == block.get_hash())

    def validate_chain(self, chain):
        """
        Validates all the blocks of a chain.

            This function is called for every newcoming node in the blockchain.
        """

        for block in chain:
            if not self.validate(block):
                return False
        return True


"""
    def valid_proof(.., difficulty=MINING_DIFFICULTY):
        # concencus functions

    def add_transaction_to_block():
        # if enough transactions  mine

    def resolve_conflicts(self):
        # resolve correct chain

"""
