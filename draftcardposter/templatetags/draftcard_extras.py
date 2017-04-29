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

@register.filter
@stringfilter
def formatvalue(value, statname):
    if statname in ('hand_size', 'arm_length', 'vert_leap', 'broad_jump'):
        return value + '"'
    elif statname in ('40_yard', 'shuttle', '3cone', '60ydshuttle'):
        return value #+ ' s'
    elif statname in ('weight_lbs',):
        return value + ' lbs'
    elif statname in ('height_in',):
        return in_to_ft_in(value)
    return value

@register.filter
def in_to_ft_in(value):
    feet, inches = divmod(int(value), 12)
    return '{0}\' {1}"'.format(feet, inches)

@register.filter 
def teamcssclass(value):
    m = value['mascot']
    if m == '49ers':
        return 'fortyniners'
    else:
        return m.lower()

@register.filter 
def ordinal_suffix(n):
  """Return the ordinal suffix for a positive integer
  >>> ordinal_suffix(0)
  ''
  >>> ordinal_suffix(1)
  'st'
  >>> ordinal_suffix(2)
  'nd'
  >>> ordinal_suffix(3)
  'rd'
  >>> ordinal_suffix(4)
  'th'
  >>> ordinal_suffix(11)
  'th'
  >>> ordinal_suffix(12)
  'th'
  >>> ordinal_suffix(13)
  'th'
  >>> ordinal_suffix(21)
  'st'
  >>> ordinal_suffix(22)
  'nd'
  >>> ordinal_suffix(23)
  'rd'
  >>> ordinal_suffix(101)
  'st'
  >>> ordinal_suffix(111)
  'th'
  >>> ordinal_suffix(112)
  'th'
  >>> ordinal_suffix(113)
  'th'
  >>> ordinal_suffix(121)
  'st'
  >>> ordinal_suffix(1111)
  'th'
  >>> ordinal_suffix(1322)
  'nd'
  >>> ordinal_suffix('horse')
  ''
  """
  try:
      n = int(n)
  except Exception:
      return ''
  if n < 1:
    return ''
  elif n >= 100:
    return ordinal_suffix(n%100)
  elif 11 <= n <= 13:
    return 'th'
  elif n%10 in (1,2,3):
    return ('st','nd','rd')[n%10-1]
  else:
    return 'th'

