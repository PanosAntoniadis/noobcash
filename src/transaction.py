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
        transaction_id (int): hash of the transaction.
        sender_address (int): the public key of the sender's wallet.
        receiver_address (int): the public key of the receiver's wallet.
        amount (int): the amount of nbc to transfer.
        transaction_inputs (list): list of TransactionInput.
        transaction_outputs (list): list of TransactionOutput.
        signature (int): signature that verifies that the owner of the wallet created the transaction.
    """

    def __init__(self, sender_address, receiver_address, amount, transaction_inputs, nbc_sent, transaction_id=None, transaction_outputs=None, signature=None):
        # nbc_sent is the amount of money that the sender send for the transaction.
        # Equals the sum of the amounts of the transaction inputs.

        self.sender_address = sender_address
        self.receiver_address = receiver_address
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

    @classmethod
    def from_dict(cls, transaction_dict, outputs):
        sender_address = transaction_dict["sender_address"]
        receiver_address = transaction_dict["receiver_address"]
        amount = transaction_dict["amount"]
        transaction_inputs = transaction_dict["transaction_inputs"]
        nbc_sent = transaction_dict["nbc_sent"]
        transaction_id = transaction_dict["transaction_id"]
        signature = transaction_dict["signature"]

        return cls(sender_address, receiver_address, amount, transaction_inputs, nbc_sent, transaction_id, outputs, signature)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __eq__(self, other):
        """
        Two transactions are equal if their current_hash is equal
        """
        return self.transaction_id == other.transaction_id

    def compute_transaction_output(self):
        # Compute the outputs of the transaction, if its not set.
        # - output for the nbcs sent to the receiver.
        # - output for the nbcs sent back to the sender as change.
        reciever_output = TransactionOutput(
            self.transaction_id, self.receiver_address, self.amount)
        self.transaction_outputs = [reciever_output]

        if self.nbc_sent > self.amount:
            # If there is change for the transaction.
            sender_output = TransactionOutput(
                self.transaction_id, self.sender_address, self.nbc_sent - self.amount)
            self.transaction_outputs.append(sender_output)

    def get_hash(self):
        """
        Computes the hash of the transaction.
        """

        ### ATTENTION ####
        # Here, instead of computing the hash in the dump of the object, we
        # generate a random number. I did this because I think this hash is just
        # a unique id and is not used in any authentication. In the dump, problems
        # occured becasuse RSA objects are not JSON serializable. CHECK AGAIN !!

        # SOLUTION
        # it is used when we sign a transaction

        # Return a random integer, at most 128 bits long.
        return Crypto.Random.get_random_bytes(128).decode("ISO-8859-1")

    def sign_transaction(self, private_key):
        """
        Sign the current transaction with the given private key.
        """
        message = self.transaction_id.encode("ISO-8859-1")
        key = RSA.importKey(private_key.encode("ISO-8859-1"))
        h = SHA256.new(message)
        signer = pss.new(key)
        self.signature = signer.sign(h).decode('ISO-8859-1')

    def verify_signature(self):
        """
        Verifies the signature of a transaction.
        """
        key = RSA.importKey(self.sender_address.encode('ISO-8859-1'))
        h = SHA256.new(self.transaction_id.encode('ISO-8859-1'))
        verifier = pss.new(key)
        try:
            verifier.verify(h, self.signature.encode('ISO-8859-1'))
            print("The signature is authentic.")
            return True
        except (ValueError, TypeError):
            print("The signature is not authentic.")
            return False
