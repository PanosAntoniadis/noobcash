import json
from time import time
from Crypto.Hash import SHA256
import pickle


class Block:
    """
    A block in the blockchain.

    Attributes:
        index (int): the sequence number of the block.
        timestamp (float): timestamp of the creation of the block.
        transactions (list): list of all the transactions in the block.
        nonce (int): the solution of proof-of-work.
        previous_hash (hash object): hash of the previous block in the blockchain.
        current_hash (hash object): hash of the block.
    """

    def __init__(self, index, previous_hash):
        """Inits a Block"""
        self.index = index
        self.timestamp = time()
        self.transactions = []
        self.nonce = None
        self.previous_hash = previous_hash
        self.current_hash = None

    def __str__(self):
        """Returns a string representation of a Block object"""
        return str(self.__class__) + ": " + str(self.__dict__)

    def __eq__(self, other):
        """Overrides the default method for comparing Block objects.

        Two blocks are equal if their current_hash is equal.
        """

        return self.current_hash == other.current_hash

    def get_hash(self):
        """Computes the current hash of the block."""

        # We should compute current hash without using the
        # field self.current_hash.
        block_list = [self.timestamp, [
            tr.transaction_id for tr in self.transactions], self.nonce, self.previous_hash]

        block_dump = json.dumps(block_list.__str__())
        return SHA256.new(block_dump.encode("ISO-8859-2")).hexdigest()

    def add_transaction(self, transaction, capacity):
        """Adds a new transaction in the block."""

        self.transactions.append(transaction)
        if len(self.transactions) == capacity:
            return True

        return False
