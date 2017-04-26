from django.db import models
import json

class Player(models.Model):
    POSITIONS = (
            ('QB', 'Quarterback'),
            ('WR', 'Wide Reciever'),
            ('CB', 'Cornerback'),
            ('K', 'Kicker'),
            ('P', 'Punter'),
            ('LS', 'Long Snapper'),
            ('DE', 'Defensive End'),
            ('ILB', 'Inside Linebacker'),
            ('DT', 'Defensive Tackle'),
            ('RB', 'Runningback'),
            ('OT', 'Offensive Tackle'),
            ('OG', 'Offensive Guard'),
            ('TE', 'Tight end'),
            ('S', 'Safety'),
            ('LB', 'Linebacker'),
            ('C', 'Center'),
            ('FB', 'Fullback'),
            ('DB', 'Defensive Back'),
            ('OLB', 'Outside Linebacker'),
            ('OL', 'Offensive Lineman'),
            ('SS', 'Strong Safety'),
            ('DL', 'Defensive Lineman'),
            ('NT', 'Nose Tackle'),
            ('FS', 'Free Safety'),
            )

    name = models.CharField(max_length=100)
    position = models.CharField(max_length=3, choices=POSITIONS)
    college = models.CharField(max_length=100)
    data_json = models.TextField()

    @property
    def data(self):
        """JSON Structure of the player data"""
        return json.loads(self.data_json)

    @data.setter
    def data(self, value):
        print(value)
        self.data_json = json.dumps(value)

    def __str__(self):
        return "{p.name} ({p.position}), {p.college}".format(p=self)


class Settings(models.Model):
    sheet_id = models.CharField(max_length=100)
    range_def = models.CharField(max_length=100)
    last_updated = models.DateTimeField()
    subreddit = models.CharField(max_length=25)
    imguralbum = models.CharField(max_length=100)
