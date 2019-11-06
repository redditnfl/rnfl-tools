#!/usr/bin/env python3

from praw import Reddit
from jinja2 import Template

mods_template = """
{%- for group in users|batch(3) %}
#Paging mods {{ loop.index }}

    type: comment
    is_top_level: true
    is_edited: false
    moderators_exempt: false
    body (regex): ['(Ping[- ]?the[- ]?mods|Ping[- ]?everyone)(: (.*))?']
    comment: |
        {{ '{{match-body-4}}' }}
        
        ***
        
        **Please do not reply to this comment. It is only for notification purposes.**

{% for user in group %}
        /u/{{ user.name }}
{% endfor %}
{% if not loop.last %}
---
{% endif %}
{%- endfor %}
""".strip()

everyone_template = """
{%- for group in users|batch(3) %}
#Paging everyone {{ loop.index }}

    type: comment
    is_top_level: true
    is_edited: false
    moderators_exempt: false
    body (regex): ['(Ping[- ]?everyone)(: (.*))?']
    comment: |
        {{ '{{match-body-4}}' }}
        
        ***
        
        **Please do not reply to this comment. It is only for notification purposes.**

{% for user in group %}
        /u/{{ user.name }}
{% endfor %}
{% if not loop.last %}
---
{% endif %}
{%- endfor %}
""".strip()

def main():
    r = Reddit('rasherdk', ua="pingrulesgenerator")

    ignore_mods = {
            r.redditor('rnfl_robot'),
            }

    nflModsMods = set(r.subreddit('nflmods').moderator()) - ignore_mods
    nflMods = set(r.subreddit('nfl').moderator()) - ignore_mods

    exMods = list(nflModsMods - nflMods)

    def by_date(u):
        return u.date

    print(Template(mods_template).render(users=sorted(list(nflMods), key=by_date)))
    print("\n---\n")
    print(Template(everyone_template).render(users=sorted(list(exMods), key=by_date)))


if __name__ == "__main__":
    main()
