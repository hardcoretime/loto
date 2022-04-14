import random
from collections import namedtuple
from typing import List

from pytest import fixture, raises, mark

from loto import LotoGame, Card, Player, Computer

class_barrels = namedtuple('barrels', ['start', 'end', 'count_for_check'])
class_players = namedtuple('players', ['players_count', 'computers_count'])
class_card = namedtuple(
    'card', ['cell_count_in_line', 'number_count_in_line', 'max_number_count_in_lines', 'line_count']
)

BARRELS = class_barrels(1, 16, 5)
PLAYERS_SET_1 = class_players(2, 1)
PLAYERS_SET_2 = class_players(1, 1)
CARD = class_card(9, 5, 15, 3)
PLAYER_INDEX = 1


@fixture
def barrels() -> List[int]:
    return list(range(BARRELS.start, BARRELS.end))


@fixture
def player(barrels: List[int]) -> Player:
    return Player(PLAYER_INDEX, Card(barrels))


@fixture
def computer(barrels: List[int]) -> Computer:
    return Computer(PLAYER_INDEX, Card(barrels))


class TestPlayer:

    def test_player_turn(self, player: Player) -> None:
        with raises(NotImplementedError):
            player.player_turn(random.randint(BARRELS.start, BARRELS.end))

    @mark.parametrize(
        'players, computers',
        [
            (PLAYERS_SET_1.players_count, PLAYERS_SET_1.computers_count),
            (PLAYERS_SET_2.players_count, PLAYERS_SET_2.computers_count),
        ]
    )
    def test_check_number_of_players(self, players: int, computers: int) -> None:
        assert Player.check_number_of_players(players, computers)

    @mark.parametrize(
        'number', random.sample(range(BARRELS.start, BARRELS.end), BARRELS.count_for_check)
    )
    def test_find_number_index(self, player: Player, number: int) -> None:
        assert player.find_number_index(number, player.card)

    def test_display_card(self, player: Player) -> None:
        assert player.display_card() is None


class TestCard:

    def test_generate_line(self, barrels: List[int]) -> None:
        line = list(' ' * CARD.cell_count_in_line)
        line_numbers = random.sample(barrels, CARD.number_count_in_line)

        line_with_numbers = Card.generate_line(line_numbers)
        filtered_numbers = [item for item in line_with_numbers if isinstance(item, int)]

        assert len(line) == CARD.cell_count_in_line
        assert len(filtered_numbers) == CARD.number_count_in_line

    def test_get_card_numbers(self, player: Player) -> None:
        assert len(player.card.lines) == CARD.line_count


class TestComputer:

    def test_player_turn(self, barrels: List[int], computer: Computer) -> None:
        for barrel in barrels:
            computer.player_turn(barrel)

        assert computer.card.numbers_in_card == CARD.max_number_count_in_lines - CARD.max_number_count_in_lines


class TestLoto:

    @mark.parametrize(
        'players, computers',
        [
            (PLAYERS_SET_1.players_count, PLAYERS_SET_1.computers_count),
            (PLAYERS_SET_2.players_count, PLAYERS_SET_2.computers_count),
        ]
    )
    def test_init_players(self, players: int, computers: int) -> None:
        game = LotoGame(players, computers)

        for player in game.players:
            assert isinstance(player, Player)
