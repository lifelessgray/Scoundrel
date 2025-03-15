# Scoundrel
import random

from deck import Deck, Card, get_name
import re


class Scoundrel:
    def __init__(self):
        self.dungeon: Deck = Deck().shuffle()
        pruned_stack: list[Card, ...] = []
        for card in self.dungeon.stack:
            # Removing red face cards/aces
            if card.suit == 2 or card.suit == 0:
                if card.value > 10:
                    continue

            pruned_stack.append(card)
        self.dungeon.stack = pruned_stack

        self.room: list[Card | None, ...] = [None, None, None, None]
        self.weapon: Card | None = None
        self.weapon_hist: list[Card, ...] = []
        self.health = 20
        self.turn = 0

        self.destroyed_cards: list[Card, ...] = []

        self.skipped_last_turn: bool = False
        self.consumed_health_this_turn: bool = False
        self.alive = True
        self.final_room = False
        self.won = False

    def start_turn(self, skipped_last: bool = False):
        self.turn += 1
        self.skipped_last_turn = skipped_last
        self.consumed_health_this_turn = False
        for i in range(len(self.room)):
            if self.room[i] is None:
                self.room[i] = self.dungeon.draw(1)[0]

        return self

    def live_cards(self) -> int:
        return len(self.room) - self.room.count(None)

    def avoid(self) -> bool:
        if self.skipped_last_turn | (self.live_cards() < len(self.room)):
            return False
        self.dungeon.bury([card for card in self.room if card is not None])
        self.room = [None, None, None, None]
        self.start_turn(True)
        return True

    def modify_health(self, count: int) -> None:
        self.health += count
        if self.health > 20:
            self.health = 20
        if self.health <= 0:
            self.alive = False

    def equip(self, card: Card) -> None:
        # Clearing out old cards
        self.destroyed_cards += self.weapon_hist + [self.weapon]
        self.weapon_hist = []

        self.weapon = card

    def fight(self, card: Card, bare: bool) -> None:
        try:
            block: int = self.weapon.value
        except AttributeError:
            block: int = 0
        try:
            last_monster: int = self.weapon_hist[-1].value
        except IndexError:
            last_monster: int = 0
        expected_damage = card.value

        if bare:
            self.modify_health(-card.value)
        else:
            if (expected_damage >= last_monster) & (last_monster > 0):
                self.modify_health(-card.value)
            else:
                self.modify_health(min(block - expected_damage, 0))
                if self.weapon is not None:
                    self.weapon_hist.append(card)

        self.destroyed_cards.append(card)

    def consume_card(self, card: Card, bare_if_fight: bool = False) -> bool:
        match card.suit:
            # Heart (Health)
            case 0:
                if not self.consumed_health_this_turn:
                    self.modify_health(card.value)
                    self.consumed_health_this_turn = True
            # Diamond (Weapon)
            case 2:
                self.equip(card)
            # Club | Spade (Monster)
            case 1 | 3:
                self.fight(card, bare_if_fight)

        self.destroyed_cards.append(card)
        return True

    def interact(self, place: int, bare_if_fight: bool = False) -> None:
        card = self.room[place]
        if self.consume_card(card, bare_if_fight):
           self.room[place] = None
        if len(self.dungeon.stack) == 0:
            self.final_room = True
        if not self.final_room:
            if self.live_cards() == 1:
                self.start_turn()
        else:
            if self.live_cards() == 0:
                self.win()

    def draw(self):
        print(f"––– Room {self.turn}")
        pretty_print(" ".join([convert(x).rjust(3, ' ') for x in self.room]) + f" [{str(self.health).rjust(2, '0')}]")
        beginning: str = f"D{str(len(self.dungeon.stack))}  "\
                         f"\033[94m{get_name(self.weapon).ljust(3, ' ') if self.weapon is not None else '[ ]'}\033[0m  "
        try:
            beginning += get_name(self.weapon_hist[-1])
        except IndexError:
            beginning += "[ ]"

        pretty_print(beginning)

    def win(self):
        self.won = True

def ANSI_sanitize(s: str) -> str:
    # ANSI is fucked and I can't be bothered to do the coloring another way or
    # create separate funcitons to get text with/without color.
    # Regex, my beloved <3
    return re.sub("\\033\[\d+m", "", s)
def convert(x):
    if x is not None:
        return get_name(x).rjust(3, " ")
    else:
        return "[ ]"

def pretty_print(s: str, count: int = 20):
    truelen = len(ANSI_sanitize(s))
    print(f" | {s}{(count-truelen)*' '} |")

def notify_print(s: str):
    print(f"\033[93m{s}\033[0m")

def how_to_play():
    print("––– Room 3\n | 8\033[91mH\033[0m 5\033[90mS\033[0m 7\033[90mC\033[0m 6\033[91mD\033[0m [14]     |\n | D34  \033[94m2\033[91mD\033[0m  [ ]         |")
    print("The first line is the current Room number.")
    print("The second shows each card in the room, (8\033[91mH\033[0m 5\033[90mS\033[0m 7\033[90mC\033[0m 6\033[91mD\033[0m)\nwith the final bracketed number being your \033[91mhealth\033[0m. (14) It may never be above 20.")
    print("The third contains three values:\n\tD, (34) the number of cards left in the Dungeon.\n\tA card representing your \033[94mweapon\033[0m (2),\n\tand a card representing the last \033[90mMonster\033[0m (Empty) you killed using it.\n")
    print("Each turn, you must interact with one of the four cards in the Room. To do so, type the number of that card 1 -> 4.")
    print("When there is only one card left, you move on to the next Room.")
    print("If a Room seems impossible, or you wish to save it for later, you may choose to avoid the Room by typing \"avoid,\" \"run,\" or \"r\".\n\tYou may avoid as many Rooms as you want, but never two in a row and never after interacting with a card.")
    print("\tThe Room's cards will be placed on the bottom of the Dungeon.")
    print("The results of interacting with a card are as follows:")
    print("If you chose to interact with a Potion (Heart):")
    print("\tYou gain health equal to the card's value.\n\tIf this would put you over 20, you are set to 20.\n\tYou may only consume one Potion per Room, consuming another will do nothing.")
    print("If you chose to interact with a Weapon (Diamond):")
    print("\tIt replaces your previous weapon (if any.)\n\tAny Monsters killed by the previous weapon are removed.")
    print("If you chose to interact with a Monster (Spade or Club):")
    print("\tYou may choose to fight with your weapon or barehanded. Typing \"b\" after your interact command will fight a Monster barehanded.")
    print("\tIf you chose barehanded:")
    print("\t\tThe Monster's full value is subtracted from your health. Aces are high cards, worth 14.")
    print("\tOtherwise:")
    print("\t\tYour health is reduced by the Monster's value plus your weapon's value.")
    print("\t\tYou do not lose your weapon until you replace it; however:\n\t\tthe weapon can only be used to slay Monsters of lesser value than the previous Monster.")
    print("\t\tIf you attempt to fight a higher valued Monster, it will deal full damage to you.")
    print("To see this guide again, use the \"help\" or \"h\" commands.")
    print("To close the game, use the \"quit\" or \"q\" commands.")

def loop():
    print("")
    game = Scoundrel().start_turn()
    run = True
    while game.alive and not game.won and run:
        game.draw()

        # noooo, I didn't get lazy for the commands,
        # what makes you say that?~
        command: str = input("Command: ")
        try:
            interact = int(str(command).removesuffix("b"))
            if interact > len(game.room):
                notify_print(f"{interact} is too large.")
                continue
            elif interact < 1:
                notify_print(f"{interact} is too small.")
                continue
            if game.room[interact-1] is None:
                notify_print("There is no card there.")
                continue
            game.interact(interact-1, command.endswith("b"))
        except ValueError:
            match str(command):
                case "avoid" | "run" | "r":
                    if not game.avoid():
                        notify_print(random.choice([
                            "You can't run now.",
                            "Can't leave yet.",
                            "You're not finished here.",
                        ]))
                case "help" | "h":
                    how_to_play()
                case "quit" | "q":
                    run = False
                case _:
                    notify_print("Not a recognized command.")
    if not game.alive:
        print("\033[91m" + random.choice([
            "A shame, really.",
            "Unfortunate.",
            "Unlucky.",
            "Nasty hit. Maybe your skull will fare better next time?",
            "Died too young.",
            "Not the best choice, was that?",
            "Dead men tell no tales.",
            "Not much left of you.",
        ]) + "\033[0m")

    if game.won:
        print("The \033[93msunlight\033[0m warms your face as you step out of the \033[91mdungeon\033[0m.")

    play_again = False
    if not game.alive or game.won:
        answered = False
        while not answered:
            ans = input("Play again? [Y/n]: ")
            ans = ans.lower()
            match ans:
                case "y" | "yes":
                    answered = True
                    play_again = True
                case "n" | "no":
                    answered = True
                case _:
                    print("Not a recognized answer.")

    if play_again:
        loop()

if __name__ == "__main__":
    how_to_play()
    loop()
