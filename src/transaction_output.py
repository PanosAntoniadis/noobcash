
class TransactionOutput:
    """
    A transaction output of a noobcash transaction.

    Attributes:
        transaction_id (int): id of the transaction.
        recipient (int): the recipient of the transaction.
        amount (int): the amount of nbcs to be transfered.
        unspent (boolean): false if this output has been used as input in a transaction.
    """

    def __init__(self, transaction_id, recipient, amount):
        """Inits a TransactionOutput."""
        self.transaction_id = transaction_id
        self.recipient = recipient
        self.amount = amount
        self.unspent = True

    @classmethod
    def fromdict(cls, output_dict):
        """Inits a TransactionOutput object given a dictionary."""
        transaction_id = output_dict["transaction_id"]
        recipient = output_dict["recipient"]
        amount = int(output_dict["amount"])
        return cls(transaction_id, recipient, amount)

    def __str__(self):
        """Returns a string representation of a TransactionOutput object"""
        return str(self.__dict__)
