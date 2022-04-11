#!/usr/bin/env python3
import logging
import random
import sys
from abc import abstractmethod
from typing import List, Tuple, Optional

import click

from rules import RULES


class Card:
    __CELL_COUNT_IN_LINE = 9
    __NUMBER_COUNT_IN_LINE = 5
    __MAX_NUMBER_COUNT_IN_LINES = 15

    def __init__(self, barrels: List[int]):
        self.lines = self.get_card_numbers(barrels)
        self.numbers_in_card = self.__class__.__MAX_NUMBER_COUNT_IN_LINES

    @classmethod
    def get_card_numbers(cls, numbers: List[int]) -> List[List]:
        card_numbers = random.sample(numbers, cls.__MAX_NUMBER_COUNT_IN_LINES)

        line_1_numbers = sorted(random.sample(card_numbers, cls.__NUMBER_COUNT_IN_LINE))
        line_2_numbers = sorted(
            random.sample(list(set(card_numbers) - set(line_1_numbers)), cls.__NUMBER_COUNT_IN_LINE)
        )
        line_3_numbers = sorted((list(set(card_numbers) - set(line_1_numbers) - set(line_2_numbers))))

        return [
            cls.generate_line(line_1_numbers),
            cls.generate_line(line_2_numbers),
            cls.generate_line(line_3_numbers),
        ]

    @classmethod
    def generate_line(cls, numbers: List[int]) -> List:
        line = list(' ' * cls.__CELL_COUNT_IN_LINE)
        random_indexes = sorted(random.sample(range(0, cls.__CELL_COUNT_IN_LINE), cls.__NUMBER_COUNT_IN_LINE))

        for index, number in zip(random_indexes, numbers):
            line[index] = number

        return line

    def __str__(self):
        return f'{self.__class__.__name__}({self.lines})'


class Player:
    __MIN_COUNT = 2

    def __init__(self, index: int, card: Card):
        self.active_status = True
        self.name = f'{self.__class__.__name__}_{index}'
        self.card = card

    def display_card(self) -> None:
        print('-' * 50)
        print(f"{self.name}'s card:")
        print(*self.card.lines, sep='\n')
        print('-' * 50)

    @abstractmethod
    def player_turn(self, barrel: int):
        raise NotImplementedError

    @staticmethod
    def find_number_index(number, card: Card) -> Optional[Tuple[int, int]]:
        for line_index, line in enumerate(card.lines):
            if number in line:
                return line_index, line.index(number)

        return None

    @classmethod
    def check_number_of_players(cls, players_count: int, computers_count: int) -> bool:
        return players_count + computers_count >= cls.__MIN_COUNT

    def __str__(self):
        return f'{self.__class__.__name__}({self.name}, {self.card})'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'


class Computer(Player):
    def __init__(self, index: int, card: Card):
        super().__init__(index, card)

    def player_turn(self, barrel: int):
        number_index = self.find_number_index(barrel, self.card)

        if number_index:
            line, index = number_index
            self.card.lines[line][index] = '-'
            self.card.numbers_in_card -= 1


class User(Player):
    def __init__(self, index: int, card: Card):
        super().__init__(index, card)

    def player_turn(self, barrel: int):
        number_index = self.find_number_index(barrel, self.card)

        player_choice = self.__get_answer()

        if number_index and player_choice == 'y':
            line, index = number_index
            self.card.lines[line][index] = '-'
            self.card.numbers_in_card -= 1

        if not number_index and player_choice == 'n':
            print('Next turn.')

        if (number_index and player_choice == 'n') or (not number_index and player_choice == 'y'):
            self.active_status = False
            print(f'{self.name}: Потрачено!')

    def __get_answer(self) -> str:
        answers = ['y', 'n']
        answer = input('Зачеркнуть цифру? (y/n)')

        if answer not in answers:
            return self.__get_answer()
        else:
            return answer


class LotoGame:
    def __init__(self, players_count: int, computers_count: int):
        self.barrels = list(range(1, 91))
        self.players = self.init_players(players_count, computers_count)

    def init_players(self, players_count: int, computers_count: int) -> List[Player]:
        players = list()

        for index in range(1, players_count + 1):
            players.append(User(index, Card(self.barrels)))

        if not computers_count:
            return players

        for index in range(1, computers_count + 1):
            players.append(Computer(index, Card(self.barrels)))

        return players


@click.command(help=RULES)
@click.option(
    '-p', '--player',
    type=click.Choice(['1', '2']),
    multiple=False,
    required=True,
    help='Minimum count of players is 1.'
)
@click.option(
    '-c', '--computer',
    type=click.Choice(['0', '1', '2']),
    default='0',
    multiple=False,
    required=False,
    help='Minimum count of computers is 0. By default: 0.'
)
def main(player: str, computer: str) -> None:
    players_count = int(player)
    computers_count = int(computer)

    if not Player.check_number_of_players(players_count, computers_count):
        logging.error('Count of players and computers must be greater than 1.')
        sys.exit(1)

    game = LotoGame(players_count, computers_count)
    random.shuffle(game.barrels)
    for index, barrel in enumerate(game.barrels):
        click.echo(f'Round: {index + 1}. Barrel: {barrel}.')
        for player in game.players:
            if player.active_status:
                player.display_card()
                player.player_turn(barrel)
            else:
                continue

            if player.card.numbers_in_card == 0:
                click.echo(f'{player.name} is winner!')
                player.display_card()
                return


if __name__ == '__main__':
    main()
