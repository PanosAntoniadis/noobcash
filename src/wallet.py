import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4


class Wallet:
    """
    The wallet of a node in the network.

    Attributes:
        public_key (int): the public key of the node (also serves as the node's address).
        private_key (int): the private key of the node.
        transactions (list): a list that contains the transactions of the node.
    """

    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key
        self.transactions = []

    def balance():
