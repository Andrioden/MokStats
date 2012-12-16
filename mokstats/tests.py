import unittest
from models import *
import datetime





class MatchPositionTestCase(unittest.TestCase):
    def setUp(self):
        place = Place.objects.create(name="Lolplace")
        
        self.player1 = Player.objects.create(name="Andre")
        self.player2 = Player.objects.create(name="Tine")
        self.player3 = Player.objects.create(name="Aase")
        
        # Match 1
        self.match1 = Match.objects.create(date=datetime.datetime.now(), place=place)
        PlayerResult.objects.create(sum_spades = 0, match=self.match1, player=self.player1, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        PlayerResult.objects.create(sum_spades = 0, match=self.match1, player=self.player2, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        PlayerResult.objects.create(sum_spades = 0, match=self.match1, player=self.player3, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        # Match 2
        self.match2 = Match.objects.create(date=datetime.datetime.now(), place=place)
        PlayerResult.objects.create(sum_spades = 1, match=self.match2, player=self.player1, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        PlayerResult.objects.create(sum_spades = 0, match=self.match2, player=self.player2, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        PlayerResult.objects.create(sum_spades = 0, match=self.match2, player=self.player3, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        # Match 3
        self.match3 = Match.objects.create(date=datetime.datetime.now(), place=place)
        PlayerResult.objects.create(sum_spades = 1, match=self.match3, player=self.player1, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        PlayerResult.objects.create(sum_spades = 1, match=self.match3, player=self.player2, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        PlayerResult.objects.create(sum_spades = 0, match=self.match3, player=self.player3, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        # Match 4
        self.match4 = Match.objects.create(date=datetime.datetime.now(), place=place)
        PlayerResult.objects.create(sum_spades = 11, match=self.match4, player=self.player1, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        PlayerResult.objects.create(sum_spades = 22, match=self.match4, player=self.player2, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        PlayerResult.objects.create(sum_spades = 33, match=self.match4, player=self.player3, sum_queens = 0,sum_solitaire_lines = 0,sum_solitaire_cards = 0,sum_pass = 0,sum_grand = 0,sum_trumph = 0)
        
        
    def test_get_position(self):
        # Match 1
        self.assertEqual(self.match1.get_position(self.player1.id), 1)
        self.assertEqual(self.match1.get_position(self.player2.id), 1)
        self.assertEqual(self.match1.get_position(self.player3.id), 1)
        # Match 2
        self.assertEqual(self.match2.get_position(self.player1.id), 3)
        self.assertEqual(self.match2.get_position(self.player2.id), 1)
        self.assertEqual(self.match2.get_position(self.player3.id), 1)
        # Match 3
        self.assertEqual(self.match3.get_position(self.player1.id), 2)
        self.assertEqual(self.match3.get_position(self.player2.id), 2)
        self.assertEqual(self.match3.get_position(self.player3.id), 1)
        # Match 4
        self.assertEqual(self.match4.get_position(self.player1.id), 1)
        self.assertEqual(self.match4.get_position(self.player2.id), 2)
        self.assertEqual(self.match4.get_position(self.player3.id), 3)