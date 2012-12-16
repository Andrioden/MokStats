import random
import unittest
from rating import RatingCalculator, RatingResult

class TestRatingCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = RatingCalculator()
        
    def testWin(self):
        results = [RatingResult("Andriod", 100, 1),
                   RatingResult("Tine", 100, 2),
                   RatingResult("Ole", 100, 3),
                   RatingResult("Johnny", 100, 4)
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
                
if __name__ == '__main__':
    unittest.main()