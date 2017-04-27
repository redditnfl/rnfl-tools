from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def statname(value):
    statnames = {
            'hand_size': 'Hand Size',
            'arm_length': 'Arm Length',
            'wonderlic': 'Wonderlic',
            '40_yard': '40 yd dash',
            'bench_press': 'Bench Press Reps',
            'vert_leap'   : 'Vert. Leap',
            'broad_jump': 'Broad Jump',
            'shuttle': 'Short Shuttle',
            '3cone': '3-cone drill',
            '60ydshuttle': '60 yard shuttle',
            }
    if value in statnames:
        return statnames[value]
    else:
        return value.replace("_", " ").title()

