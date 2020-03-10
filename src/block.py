from time import time
from Crypto.Hash import SHA256
import json


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
        self.current_hash = myHash()

    def get_hash(self):
        return SHA256.new(self.index + self.previousHash + self.timestamp + JSON.stringify(self.transactions) + self.nonce).hexdigest()

    def add_transaction(self, transaction):
        """
        Adds a new transaction in the block.
        """

        self.transactions.append(transaction)
