
class TransactionInput:
    """
    The transaction input of a noobcash transaction.

    Attributes:
        previous_output_id (int): id of the transaction that the coins come from.
    """

    def __init__(self, previous_output_id):
        self.previous_output_id = previous_output_id
