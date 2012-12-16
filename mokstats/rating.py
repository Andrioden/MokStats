from decimal import *

K = Decimal('10.0')
START_RATING = Decimal('100.0')

class RatingCalculator:
    def __init__(self):
        pass
    def new_ratings(self, players):
        total_rating = sum([p.rating for p in players])
        points_for_position = range(len(players)-1,-1,-1)
        total_points = sum(points_for_position)
        #print total_rating
        #print points_for_position
        #print total_points
        for p in players:
            from_rating = p.rating
            #print p.rating, total_rating
            win_chance = p.rating/total_rating
            expected_points = total_points * win_chance
            actual_points = points_for_position[p.position-1]
            p.rating += K * (actual_points - expected_points)
            #print "(%s) %s - Win chance of %s and position %s, gives expected / actual points of %s/%s and %s as new rating " % (p.dbid, round(from_rating,2), round(win_chance,2), p.position, round(expected_points,2), actual_points, round(p.rating,2))
        return players
        
    

        
class RatingResult:
    dbid = None
    rating = None
    position = None
    def __init__(self, dbid, rating, position):
        self.dbid = dbid
        self.rating = rating
        self.position = position