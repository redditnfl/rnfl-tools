from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import last_modified
from django.utils.decorators import method_decorator
from datetime import datetime, timezone
from pprint import pprint
from django.views import generic, View

from .models import Player, Settings
from .ajaxmixin import AJAXListMixin, AJAXSingleObjectMixin

from draftcards.draftcards import massage_values
from draftcards.sheets import GoogleSheetsData
from draftcards.render import Render
from draftcards.screenshot import Screenshot
import nflteams
from django.db import transaction

def add_common_context(context):
    context['positions'] = Player.POSITIONS
    context['teams'] = sorted(nflteams.fullinfo.items(), key=lambda v: v[1]['fullname'])
    context['rounds'] = range(1, 8)
    return context

def latest_update(*args, **kwargs):
    return Settings.objects.all()[0].last_updated

@method_decorator(login_required, name='dispatch')
class IndexView(generic.TemplateView):
    template_name = 'draftcardposter/index.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super(IndexView, self).get_context_data(*args, **kwargs)
        return add_common_context(context_data)

@method_decorator(last_modified(latest_update), name='dispatch')
class PlayerList(AJAXListMixin, generic.ListView):
    model = Player
    context_object_name = 'players'

@method_decorator(last_modified(latest_update), name='dispatch')
class PlayerDetail(AJAXSingleObjectMixin, generic.DetailView):
    model = Player
    context_object_name = 'player'

@method_decorator(transaction.atomic, name='dispatch')
class UpdatePlayers(View):

    def get(self, request, *args, **kwargs):
        settings = Settings.objects.all()[0]
        pprint(settings)
        sheets = GoogleSheetsData(settings.sheet_id, parseargs=False)
        Player.objects.all().delete()
        players = sheets.get_range_dict(settings.range_def)
        i = 0
        for player in players:
            import json
            p = Player(name=player['name'], position=player['pos'], college=player['college'], data_json=json.dumps(player))
            player = massage_values(player)
            del(player['name'])
            del(player['pos'])
            del(player['college'])
            p.data = player
            p.save()
            i += 1
        context = add_common_context({'msg': 'Updated %d player%s' % (i, '' if i==1 else 's')})
        settings.last_updated = datetime.now(timezone.utc)
        settings.save()
        from django.db import connection
        pprint(connection.queries)
        return render(request, 'draftcardposter/index.html', context=context)

def player_if_found(name, college):
    players = Player.objects.filter(name=name, college=college)
    if len(players) == 1:
        return players[0]

@method_decorator(login_required, name='dispatch')
class PreviewPost(View):

    def post(self, request, *args, **kwargs):
        player = player_if_found(name=request.POST.get('name', ''), college=request.POST.get('college', ''))
        pprint(request.POST)
        pprint(player)
        context = {
            'player': player,
            'team': nflteams.fullinfo[request.POST.get('team', '')],
            }
        for k in ('name', 'college', 'position', 'round', 'pick'):
            context[k] = request.POST.get(k, '')
        context = add_common_context(context)
        return render(request, 'draftcardposter/preview.html', context=context)

def split_name(name):
    return name.split(' ', 1)

def ordinal(num):
    lastdigit = int(num[-1])
    if lastdigit == 1:
        return 'st'
    elif lastdigit == 2:
        return 'nd'
    elif lastdigit == 3:
        return 'rd'
    else:
        return 'th'

class PlayerCard(View):

    def get(self, request, overall, team, pos, name, college, fmt, *args, **kwargs):
        if fmt == 'png':
            sshot = Screenshot(1300, 1300)
            url = reverse('player-card', kwargs={'overall':overall, 'team':team, 'pos':pos, 'name':name, 'college':college, 'fmt':'html'})
            fullurl = request.build_absolute_uri(url)
            print(url)
            print(fullurl)
            png = sshot.sshot_url_to_png(fullurl)
            return HttpResponse(png, content_type="image/png")
        else:
            player = player_if_found(name, college)
            firstname, lastname = split_name(name)
            context = {
                    'p': player,
                    'position': pos,
                    'position_long': dict(Player.POSITIONS)[pos],
                    'ordinal': ordinal(overall),
                    'overall': overall,
                    'name': name,
                    'firstname': firstname,
                    'lastname': lastname,
                    'college': college,
                    'photo': 'draftcardposter/img/' + player.data['filename'] + '.jpg',
                    }
            return render(request, 'draftcardposter/card-layout.html', context=context)
