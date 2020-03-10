from collections import OrderedDict
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


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

    def __init__(self, sender_address, receiver_address, amount, transaction_inputs, nbc_sent):
        # nbc_sent is the amount of money that the sender send for the transaction.
        # Equals the sum of the amounts of the transaction inputs.

        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.transaction_inputs = transaction_inputs

        # Compute the outputs of the transaction.
        # - output for the nbcs sent to the receiver.
        # - output for the nbcs sent back to the sender as change.

        reciever_output = TransactionOutput(
            self.transaction_id, receiver_address, amount)
        self.transaction_outputs = [reciever_output]
        if nbc_sent > amount:
            # If there is change for the transaction.
            sender_output = TransactionOutput(
                self.transaction_id, sender_address, nbc_sent - amount)
            self.transaction_outputs.append(sender_output)

        self.transaction_id = self.get_hash()
        self.signature = None

    def get_hash(self):
        """
        Compute the hash of the current transaction.
        """
        return SHA256.new(self.sender_address + self.receiver_address + self.amount).hexdigest()

    def sign_transaction(self, private_key):
        """
        Sign the current transaction with the given private key.
        """
        message = self.current_hash
        key = RSA.importKey(private_key)
        h = SHA.new(message)
        signer = PKCS1_v1_5.new(key)
        self.signature = signer.sign(h)

    def verify_signature(self):
        """
        Verifies the signature of a transaction.
        """
        key = RSA.importKey(self.sender_address)
        h = SHA.new(self.current_hash)
        verifier = PKCS1_v1_5.new(key)
        if verifier.verify(h, self.signature):
            return True
        else:
            print False
