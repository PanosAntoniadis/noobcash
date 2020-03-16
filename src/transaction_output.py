
class TransactionOutput:
    """
    A transaction output of a noobcash transaction.

    Attributes:
        transaction_id (int): id of the transaction.
        recipient (int): the recipient of the transaction.
        amount (int): the amount of nbcs to be transfered.
    """

    def __init__(self, transaction_id, recipient, amount):
        self.transaction_id = transaction_id
        self.recipient = recipient
        self.amount = amount
        self.unspent = True

    def __str__(self):
        return str(self.__dict__)
