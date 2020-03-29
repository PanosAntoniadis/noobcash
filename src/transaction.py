from collections import OrderedDict
import binascii
import json

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pss

import requests
from flask import Flask, jsonify, request, render_template

from transaction_output import TransactionOutput


class Transaction:
    """
    A noobcash transaction in the blockchain

    Attributes:
        sender_address (int): the public key of the sender's wallet.
        sender_id (int): the id of the sender node.
        receiver_address (int): the public key of the receiver's wallet.
        receiver_id (int): the id of the receiver node.
        amount (int): the amount of nbc to transfer.
        transaction_inputs (list): list of TransactionInput.
        nbc_sent (int): the amount of money that the sender send for the transaction.
        transaction_id (int): hash of the transaction.
        transaction_outputs (list): list of TransactionOutput.
        signature (int): signature that verifies that the owner of the wallet created the transaction.
    """

    def __init__(self, sender_address, sender_id, receiver_address, receiver_id, amount, transaction_inputs, nbc_sent, transaction_id=None, transaction_outputs=None, signature=None):
        """Inits a Transaction"""
        self.sender_address = sender_address
        self.sender_id = sender_id
        self.receiver_address = receiver_address
        self.receiver_id = receiver_id
        self.amount = amount
        self.transaction_inputs = transaction_inputs
        self.nbc_sent = nbc_sent

        if (transaction_id):
            self.transaction_id = transaction_id
        else:
            self.transaction_id = self.get_hash()

        if (not transaction_outputs):
            self.compute_transaction_output()
        else:
            self.transaction_outputs = transaction_outputs

        self.signature = signature

    def __str__(self):
        """Returns a string representation of a Transaction object"""
        return str(self.__class__) + ": " + str(self.__dict__)

    def __eq__(self, other):
        """Overrides the default method for comparing Transaction objects.

        Two transactions are equal if their current_hash is equal.
        """

        return self.transaction_id == other.transaction_id

    def to_list(self):
        """Converts a Transaction object into o list."""
        return [self.sender_id, self.receiver_id, self.amount, self.nbc_sent, self.nbc_sent - self.amount]

    def compute_transaction_output(self):
        """Compute the outputs of the transaction, if not set.

        The computation includes:
            - an output for the nbcs sent to the receiver.
            - an output for the nbcs sent back to the sender as change.
        """

        reciever_output = TransactionOutput(
            self.transaction_id, self.receiver_address, self.amount)
        self.transaction_outputs = [reciever_output]

        if self.nbc_sent > self.amount:
            # If there is change for the transaction.
            sender_output = TransactionOutput(
                self.transaction_id, self.sender_address, self.nbc_sent - self.amount)
            self.transaction_outputs.append(sender_output)

    def get_hash(self):
        """Computes the hash of the transaction."""

        # The hash is a random integer, at most 128 bits long.
        return Crypto.Random.get_random_bytes(128).decode("ISO-8859-1")

    def sign_transaction(self, private_key):
        """Sign the current transaction with the given private key."""

        message = self.transaction_id.encode("ISO-8859-1")
        key = RSA.importKey(private_key.encode("ISO-8859-1"))
        h = SHA256.new(message)
        signer = pss.new(key)
        self.signature = signer.sign(h).decode('ISO-8859-1')

    def verify_signature(self):
        """Verifies the signature of a transaction."""

        key = RSA.importKey(self.sender_address.encode('ISO-8859-1'))
        h = SHA256.new(self.transaction_id.encode('ISO-8859-1'))
        verifier = pss.new(key)
        try:
            verifier.verify(h, self.signature.encode('ISO-8859-1'))
            return True
        except (ValueError, TypeError):
            return False
