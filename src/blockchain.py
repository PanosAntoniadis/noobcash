class Blockchain:
    """
    The blockchain of the noobcash

    Attributes:
        blocks (list): list that contains the validated blocks of the chain.
    """

    def __init__(self):
        self.blocks = []

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def add_block(self, block):
        """
        Adds a new block in the chain.
        """
        self.blocks.append(block)
