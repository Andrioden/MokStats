from decimal import *

K = Decimal('10.0')
START_RATING = Decimal('100.0')

class RatingCalculator:
    def __init__(self):
        pass
    def new_ratings(self, players):
        total_rating = sum([p.rating for p in players])
        points_for_position = self.points_for_position(players)
        total_points = sum(points_for_position)
        #unsported_positions =
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
    
    def points_for_position(self, players, ):
        """ Calculates how much each match positions awards in points, if
        no-one has the same position the for loop does nothing except, adding
        and dividing again.
        
        """
        sorted_positions = sorted([p.position for p in players])
        points = self.drange(len(players))
        for y in range(len(sorted_positions)):
            ypos = sorted_positions[y]
            shared_points = 0
            shared_by = []
            # Find sharing positions
            for i in range(len(sorted_positions)):
                ipos = sorted_positions[i]
                if ypos == ipos:
                    shared_points += points[i]
                    shared_by.append(i)
                    y = i
            # Divide sharing sum among sharers
            points_each = shared_points/len(shared_by)
            for sharer_pos in shared_by:
                points[sharer_pos] = points_each
                
            
        return points
    
    def drange(self, length):
        drange = []
        for i in range(length-1,-1,-1):
            drange.append(Decimal("%s.00" % i))
        return drange
    

        
class RatingResult:
    dbid = None
    rating = None
    position = None
    def __init__(self, dbid, rating, position):
        self.dbid = dbid
        self.rating = rating
        self.position = position