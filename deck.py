import random
from typing import Callable


class Card:
    def __init__(self, value: int, suit: int):
        self.value = value
        self.suit = suit

    def matches_value(self, other) -> bool:
        return self.value == other.value

    def matches_suit(self, other) -> bool:
        return self.suit == other.suit

def card_name_gen(value_table: dict, suit_table: dict) -> Callable:
    def card_namer(card: Card) -> str:
        name: str = ""

        face_cards = value_table
        str_value = face_cards.get(card.value)
        if str_value is None:
            str_value = str(card.value)
        name += str_value

        suit = suit_table
        str_suit = suit.get(card.suit)
        if str_suit is None:
            str_suit = str(card.suit)
        name += str_suit

        return name
    return card_namer

get_name = card_name_gen({
            1: "A",
            14: "A",
            11: "J",
            12: "Q",
            13: "K",
        }, {
            0: "\033[91mH\033[0m",#"♡",
            1: "\033[90mC\033[0m",#"♣",
            2: "\033[91mD\033[0m",#"♢",
            3: "\033[90mS\033[0m",#"♠",
        })


class Deck:
    def __init__(self, autofill: bool = True, error_on_duplicates: bool = True):
        self.stack = []
        if autofill:
            for j in range(4):
                for i in range(2, 15):
                    self.stack.append(Card(i, j))

        self.EoD = error_on_duplicates

    def shuffle(self):
        random.shuffle(self.stack)
        return self

    def in_deck(self, card: Card) -> bool:
        return card in self.stack

    def check_duplicate_error(self, cards: Card):
        if any(map(self.in_deck, cards)):
            raise Exception(f"This deck was given duplicate cards: {self}")

    def draw(self, count: int) -> list[Card, ...]:
        drawn = []
        for _ in range(count):
            try:
                drawn.append(self.stack.pop())
            except IndexError:
                drawn.append(None)
        return drawn

    def cycle(self, count: int):
        for _ in range(count):
            self.stack.insert(0, self.stack.pop())
        return self

    def stage(self, cards: list[Card, ...]) -> None:
        if self.EoD:
            self.check_duplicate_error(cards)
        self.stack += cards

    def bury(self, cards: list[Card, ...]) -> None:
        if self.EoD:
            self.check_duplicate_error(cards)
        self.stack = cards + self.stack
