import block
import wallet


class Node:
    """
    A node in the network.

    Attributes:
        chain (Blockchain): the blockchain that the node has.
        id (int): the id of the node.
        nbc (int): the noobcash coins that the node has.
        wallet (Wallet): the wallet of the node.
    """

    def __init__(self, chain, id, nbc, wallet):
        self.chain = chain
        self.id = id
        self.nbc = nbc
        self.wallet = wallet

    def create_new_block():

    def create_wallet():
        # create a wallet for this node, with a public key and a private key

    def register_node_to_ring():
        # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
        # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs

    def create_transaction(sender, receiver, signature):
        # remember to broadcast it

    def broadcast_transaction():

    def validdate_transaction():
        # use of signature and NBCs balance

    def add_transaction_to_block():
        # if enough transactions  mine

    def mine_block():

    def broadcast_block():

    def valid_proof(.., difficulty=MINING_DIFFICULTY):
        # concencus functions

    def valid_chain(self, chain):
        # check for the longer chain accroose all nodes

    def resolve_conflicts(self):
        # resolve correct chain
