import json
from time import time
from Crypto.Hash import SHA256


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

    def __init__(self, index, nonce, previous_hash):
        self.index = index
        self.timestamp = time()
        self.transactions = []
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.current_hash = self.get_hash()

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def get_hash(self):
        """
        Computes the current hash of the block.
        """

        # Convert the block object into a JSON string and hash it.
        block_dump = json.dumps(self.__dict__, sort_keys=True)
        return SHA256.new(block_dump.encode()).hexdigest()

    def add_transaction(self, transaction):
        """
        Adds a new transaction in the block.
        """

        self.transactions.append(transaction)
