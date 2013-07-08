from decimal import Decimal
from models import cur_config

class RatingCalculator:
    def __init__(self):
        self.K = cur_config().rating_k
    def new_ratings(self, players):
        total_rating = sum([p.rating for p in players])
        points_for_position = self.points_for_position(players)
        total_points = sum(points_for_position)
        #unsported_positions =
        #print total_rating
        #print points_for_position
        #print total_points
        for p in players:
            #from_rating = p.rating
            win_chance = p.rating/total_rating
            expected_points = total_points * win_chance
            actual_points = points_for_position[p.position-1]
            p.rating += self.K * (actual_points - expected_points)
            #print "(%s) %s - Win chance of %s and position %s, gives expected/actual points of %s/%s and %s as new rating " % (p.dbid, round(from_rating,2), round(win_chance,2), p.position, round(expected_points,2), actual_points, round(p.rating,2))
        return players
    
    def points_for_position(self, players):
        """ Calculates how much each match positions awards in points, if
        no-one has the same position the for loop does nothing except adding
        and dividing again. The match position to point mapping works as following:
        A total amount of point fluxation is calculated, this defines how much points
        is lost and gained totaly among all players. Then the point fluxation is 
        divided among all positions, starting with max and ending with 0.
        
        """
        # Create the normal position to point mapping
        # Change this part if the balance between position, player count and points awarded
        # needs to be changed.
        point_flux = self.K * 2 # Total amount of points in movement for 1 match
        points_parts = sum([i for i in range(len(players))])
        points = []
        for i in reversed(range(len(players))):
            points.append(Decimal(point_flux * i / points_parts)) # Postion to Point mapping
        # Check if someone has matching positions, then rework the mapping.
        sorted_positions = sorted([p.position for p in players])
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
        
class RatingResult:
    dbid = None
    rating = None
    position = None
    def __init__(self, dbid, rating, position):
        self.dbid = dbid
        self.rating = rating
        self.position = position