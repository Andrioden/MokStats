import random
import unittest
from decimal import *

from rating import RatingCalculator, RatingResult

class TestRatingCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = RatingCalculator()
        
    def testWin(self):
        results = [RatingResult("Andriod", Decimal('100.0'), 1),
                   RatingResult("Tine", Decimal('100.0'), 2),
                   RatingResult("Ole", Decimal('100.0'), 3),
                   RatingResult("Johnny", Decimal('100.0'), 4)
                   ]
        new_player_ratings = self.calc.new_ratings(results)
        for p_rating in new_player_ratings:
            if p_rating.dbid == "Andriod":
                self.assertEqual(p_rating.rating, 115.0)
            elif p_rating.dbid == "Tine":
                self.assertEqual(p_rating.rating, 105.0)
            elif p_rating.dbid == "Ole":
                self.assertEqual(p_rating.rating, 95.0)
            elif p_rating.dbid == "Johnny":
                self.assertEqual(p_rating.rating, 85.0)
                
    def testDraw(self):
        results = [RatingResult("Andriod", Decimal('100.0'), 4),
                   RatingResult("Tine", Decimal('100.0'), 2),
                   RatingResult("Ole", Decimal('100.0'), 2),
                   RatingResult("Johnny", Decimal('100.0'), 1)
                   ]
        new_player_ratings = self.calc.new_ratings(results)
        for p_rating in new_player_ratings:
            if p_rating.dbid == "Andriod":
                self.assertEqual(p_rating.rating, 85.0)
            elif p_rating.dbid == "Tine":
                self.assertEqual(p_rating.rating, 100.0)
            elif p_rating.dbid == "Ole":
                self.assertEqual(p_rating.rating, 100.0)
            elif p_rating.dbid == "Johnny":
                self.assertEqual(p_rating.rating, 115.0)
                
    def testDraw2(self):
        results = [RatingResult("Andriod", Decimal('100.0'), 1),
                   RatingResult("Tine", Decimal('100.0'), 1),
                   RatingResult("Ole", Decimal('100.0'), 3),
                   RatingResult("Johnny", Decimal('100.0'), 4)
                   ]
        new_player_ratings = self.calc.new_ratings(results)
        for p_rating in new_player_ratings:
            if p_rating.dbid == "Andriod":
                self.assertEqual(p_rating.rating, 110.0)
            elif p_rating.dbid == "Tine":
                self.assertEqual(p_rating.rating, 110.0)
            elif p_rating.dbid == "Ole":
                self.assertEqual(p_rating.rating, 95.0)
            elif p_rating.dbid == "Johnny":
                self.assertEqual(p_rating.rating, 85.0)
if __name__ == '__main__':
    unittest.main()