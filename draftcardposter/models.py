from django.db import models
import json

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

class Player(models.Model):
    POSITIONS = POSITIONS

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
    prio_range_def = models.CharField(max_length=100)
    posting_enabled = models.BooleanField(default=True)


class Priority(models.Model):
    POSITIONS = POSITIONS
    position = models.CharField(max_length=3, choices=POSITIONS)
    prio1 = models.CharField(max_length=30)
    prio2 = models.CharField(max_length=30)
    prio3 = models.CharField(max_length=30)
    prio4 = models.CharField(max_length=30)

    def __str__(self):
        return "{p.position}: {p.prio1}, {p.prio2}, {p.prio3}, {p.prio4}".format(p=self)

    def as_list(self):
        r = []
        if self.prio1:
            r.append(self.prio1)
        if self.prio2:
            r.append(self.prio2)
        if self.prio3:
            r.append(self.prio3)
        if self.prio4:
            r.append(self.prio4)
        return r

    def merge_with(self, other):
        m = self.as_list()
        for p in other.as_list():
            if p not in m:
                m.append(p)
        self.prio1 = m[0] if len(m) > 0 else None
        self.prio2 = m[1] if len(m) > 1 else None
        self.prio3 = m[2] if len(m) > 2 else None
        self.prio4 = m[3] if len(m) > 3 else None
        return self
