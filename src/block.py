import json
from time import time
from Crypto.Hash import SHA256
import pickle

# Capacity defines the maximum number of transactions
# a block can have.
CAPACITY = 1


class Block:
    """
    A block in the blockchain.

    Attributes:
        index (int): the sequence number of the block.
        timestamp (float): timestamp of the creation of the block.
        transactions (list): list of all the transactions in the block.
        nonce (int): the solution of proof-of-work.
        current_hash (hash object): hash of the block.
        previous_hash (hash object): hash of the previous block in the blockchain.
    """

    def __init__(self, index, previous_hash):
        self.index = index
        self.timestamp = time()
        self.transactions = []
        self.nonce = None
        self.previous_hash = previous_hash
        self.current_hash = None

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __eq__(self, other):
        """
        Two blocks are equal if their current_hash is equal
        """
        return self.current_hash == other.current_hash

    def get_hash(self):
        """
        Computes the current hash of the block.
        """

        # Convert the block object into a JSON string and hash it.

        # Here, we should compute current hash without using the
        # field self.current_hash.
        block_dict = {'index': self.index,
                      'timestamp': self.timestamp,
                      'transactions': self.transactions,
                      'nonce': self.nonce,
                      'previous_hash': self.previous_hash}

        block_dump = pickle.dumps(block_dict)
        return SHA256.new(block_dump).hexdigest()

    def add_transaction(self, transaction):
        """
        Adds a new transaction in the block.
        """
        self.transactions.append(transaction)

        if len(self.transactions) == CAPACITY:
            return True

        return False
