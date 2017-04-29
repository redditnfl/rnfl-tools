#!/usr/bin/env python

FORFEITED = 'X'
MOVED = 'M'
MOVED_TO = 'm'
COMP = 'c'
UNKNOWN = '?'

PICK_FLAGS = (UNKNOWN, FORFEITED, MOVED, MOVED_TO, COMP)

def parsedrafts(s):
    drafts = {}
    for ds in s.split("---"):
        ds = ds.strip().split("\n")
        year = int(ds[0])
        draft = []
        for rs in ds[1:]:
            round_no, picks = rs.split(": ")
            rnd = []
            for ps in picks.split(","):
                flag = None
                if ps[-1] in PICK_FLAGS:
                    flag = ps[-1]
                    ps = ps[:-1]
                pick = int(ps)
                rnd.append((pick, flag))
            draft.append(rnd)
        drafts[year] = draft
    return drafts

def overall(year, t_rnd, t_pick):
    if year not in drafts:
        return -1
    draft = drafts[year]
    overall = 0
    rnd_no = 0
    for rnd in draft:
        rnd_no += 1
        for pick, flag in rnd:
            if flag is None or flag not in (FORFEITED, MOVED):
                overall += 1
            if rnd_no == t_rnd and pick == t_pick:
                return overall
    
def pick_type(year, rnd, pick):
    if year not in drafts:
        raise Exception("I don't know about draft %s" % year)
    if pick < 1 or rnd < 1:
        return UNKNOWN
    try:
        return drafts[year][rnd-1][pick-1][1]
    except Exception:
        return UNKNOWN


drafts = parsedrafts("""
2017
1: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32
2: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32
3: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33c,34c,35c,36c,37c,38c,39c,40c,41c,42c,43c
4: 1,2,3,4,5,6,7,8,9,10,11X,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32c,33c,34m,36c,37c,38c,39c
5: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26X,27,28,29,30,31,32,33c,34c,35c,36c,37c,38c,39c,40c,41c
6: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27X,28,29,30,31,32,33c,34c,35c
7: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33c,34c,35c
""")


assert overall(2017, 1, 1) == 1
assert overall(2017, 2, 1) == 33
assert overall(2017, 3, 1) == 65
assert overall(2017, 4, 1) == 108
assert overall(2017, 4, 13) == 119
assert overall(2017, 5, 1) == 145
assert overall(2017, 6, 1) == 185
assert overall(2017, 7, 1) == 219

assert pick_type(2017, 5, 0) == UNKNOWN
assert pick_type(2017, 5, 1) == None
assert pick_type(2017, 5, 25) == None
assert pick_type(2017, 5, 26) == FORFEITED
assert pick_type(2017, 5, 27) == None
assert pick_type(2017, 5, 32) == None
assert pick_type(2017, 5, 33) == COMP
assert pick_type(2017, 5, 41) == COMP
assert pick_type(2017, 5, 42) == UNKNOWN
