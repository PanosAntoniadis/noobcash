from collections import OrderedDict
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:
    """
    A noobcash transaction in the blockchain

    Attributes:
        sender_address (int): the public key of the sender's wallet.
        receiver_address (int): the public key of the receiver's wallet.
        amount (int): the amount of nbc to transfer.
        transaction_id (int): hash of the transaction.
        transaction_inputs (list): list of Transaction Input.
        transaction_outputs (list): list of Transaction Output.
    """

    def __init__(self, sender_address, receiver_address, amount, transaction_id, transaction_inputs, transaction_outputs):
        self.sender_address
        self.receiver_address
        self.amount
        self.transaction_id
        self.transaction_inputs
        self.transaction_outputs

    def to_dict(self):

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
