import blockchain


class Block:
    """
    A block in the blockchain.

    Attributes:
        index (int): the sequence number of the block.
        timestamp (int): timestamp of the creation of the block.
        transactions (list): list of the transactions in the block.
        nonce (int): the solution of proof-of-work.
        current_hash (int): hash of the block.
        previous_hash (int): hash of the previous block in the blockchain.
    """

    def __init__(self, index, timestamp, nonce, current_hash, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = []
        self.nonce = nonce
        self.current_hash = current_hash
        self.previous_hash = previous_hash

    def myHash:
        # calculate self.hash

    def add_transaction(transaction transaction, blockchain blockchain):
        # add a transaction to the block
