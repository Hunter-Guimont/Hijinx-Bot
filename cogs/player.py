class Player:
    __slots__ = ('identity', 'started', 'money', 'book')
    """Defines player object and handles the info directly liked to said player"""
    """This is the only information in the game that ever needs to be saved."""

    def __init__(self, id_, jenny, book):
        self.identity = id_
        self.money = jenny
        self.book = book

    def update_wallet(self, sum_: float):
        if sum_ < 0 and abs(sum_) > self.money:
            raise ValueError("You can't afford that!")
        self.money += sum_

