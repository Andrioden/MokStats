import unittest
from decimal import Decimal

from rating import RatingCalculator, RatingResult

class TestRatingCalculator(unittest.TestCase):
    # NOTE: Tests will fail, currently only used to check differences. Assertequals not updated.
    
    def setUp(self):
        self.calc = RatingCalculator()
        
    def testWin5players(self):
        results = [RatingResult("Andriod", Decimal('100.0'), 1),
                   RatingResult("Tine", Decimal('100.0'), 2),
                   RatingResult("Ole", Decimal('100.0'), 3),
                   RatingResult("Johnny", Decimal('100.0'), 4),
                   RatingResult("Stian", Decimal('100.0'), 5)
                   ]
        new_player_ratings = self.calc.new_ratings(results)
        for p_rating in new_player_ratings:
            if p_rating.dbid == "Andriod":
                self.assertEqual(p_rating.rating, 104.5)
            elif p_rating.dbid == "Tine":
                self.assertEqual(p_rating.rating, 101.5)
            elif p_rating.dbid == "Ole":
                self.assertEqual(p_rating.rating, 98.5)
            elif p_rating.dbid == "Johnny":
                self.assertEqual(p_rating.rating, 95.5)
            elif p_rating.dbid == "Stian":
                self.assertEqual(p_rating.rating, 95.5)
                
    def testWin4players(self):
        results = [RatingResult("Andriod", Decimal('100.0'), 1),
                   RatingResult("Tine", Decimal('100.0'), 2),
                   RatingResult("Ole", Decimal('100.0'), 3),
                   RatingResult("Johnny", Decimal('100.0'), 4)
                   ]
        new_player_ratings = self.calc.new_ratings(results)
        for p_rating in new_player_ratings:
            if p_rating.dbid == "Andriod":
                self.assertEqual(p_rating.rating, 104.5)
            elif p_rating.dbid == "Tine":
                self.assertEqual(p_rating.rating, 101.5)
            elif p_rating.dbid == "Ole":
                self.assertEqual(p_rating.rating, 98.5)
            elif p_rating.dbid == "Johnny":
                self.assertEqual(p_rating.rating, 95.5)
                
    def testWin3players(self):
        results = [RatingResult("Andriod", Decimal('100.0'), 1),
                   RatingResult("Tine", Decimal('100.0'), 2),
                   RatingResult("Ole", Decimal('100.0'), 3)]
        new_player_ratings = self.calc.new_ratings(results)
        for p_rating in new_player_ratings:
            if p_rating.dbid == "Andriod":
                self.assertEqual(p_rating.rating, 104.5)
            elif p_rating.dbid == "Tine":
                self.assertEqual(p_rating.rating, 101.5)
            elif p_rating.dbid == "Ole":
                self.assertEqual(p_rating.rating, 98.5)
                
    def testWin3players2(self):
        results = [RatingResult("Andriod", Decimal('200.0'), 1),
                   RatingResult("Tine", Decimal('100.0'), 2),
                   RatingResult("Ole", Decimal('100.0'), 3)]
        new_player_ratings = self.calc.new_ratings(results)
        for p_rating in new_player_ratings:
            if p_rating.dbid == "Andriod":
                self.assertEqual(p_rating.rating, 104.5)
            elif p_rating.dbid == "Tine":
                self.assertEqual(p_rating.rating, 101.5)
            elif p_rating.dbid == "Ole":
                self.assertEqual(p_rating.rating, 98.5)
                

    def testDraw(self):
        results = [RatingResult("Andriod", Decimal('100.0'), 4),
                   RatingResult("Tine", Decimal('100.0'), 2),
                   RatingResult("Ole", Decimal('100.0'), 2),
                   RatingResult("Johnny", Decimal('100.0'), 1)
                   ]
        new_player_ratings = self.calc.new_ratings(results)
        for p_rating in new_player_ratings:
            if p_rating.dbid == "Andriod":
                self.assertEqual(p_rating.rating, 95.5)
            elif p_rating.dbid == "Tine":
                self.assertEqual(p_rating.rating, 100.0)
            elif p_rating.dbid == "Ole":
                self.assertEqual(p_rating.rating, 100.0)
            elif p_rating.dbid == "Johnny":
                self.assertEqual(p_rating.rating, 104.5)
                
    def testDraw2(self):
        results = [RatingResult("Andriod", Decimal('100.0'), 1),
                   RatingResult("Tine", Decimal('100.0'), 1),
                   RatingResult("Ole", Decimal('100.0'), 3),
                   RatingResult("Johnny", Decimal('100.0'), 4)
                   ]
        new_player_ratings = self.calc.new_ratings(results)
        for p_rating in new_player_ratings:
            if p_rating.dbid == "Andriod":
                self.assertEqual(p_rating.rating, 103.0)
            elif p_rating.dbid == "Tine":
                self.assertEqual(p_rating.rating, 103.0)
            elif p_rating.dbid == "Ole":
                self.assertEqual(p_rating.rating, 98.5)
            elif p_rating.dbid == "Johnny":
                self.assertEqual(p_rating.rating, 95.5)


if __name__ == '__main__':
    unittest.main()