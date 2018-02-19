import re
from queue import Empty
from config import config


lp_regex = re.compile(r'\d+\.\sid=(\d+)\,\s+([a-zA-Z0-9]+),\spos=\((\-{0,1}\d+\.{0,1}\d*),\s(\-{0,1}\d+\.{0,1}\d*'
                      r'),\s(\-{0,1}\d+\.{0,1}\d)\),\srot=\(\-{0,1}\d+\.{0,1}\d*,\s\-{0,1}\d+\.{0,1}\d*,\s\-{0,1}\d+\.'
                      r'{0,1}\d*\),\sremote=(?:True|False),\shealth=(\d+),\sdeaths=(\d+),\szombies=(\d+),\splayers=(\d+)'
                      r',\sscore=(\d+),\slevel=(\d+),\ssteamid=(\d+),\sip=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}),\sping='
                      r'(\d+)')
lp_end_regex = re.compile(r'Total\sof\s\d+\sin\sthe\sgame')


def player_list(console):
    console.send_command('lp')
    players_dict = dict()
    while True:
        try:
            line = console.get_line()
            #if config['debug']: print('got line "{}"'.format(line))
        except Empty as e:
            break
        if lp_end_regex.match(line) is not None:
            if config['debug']: print('found end of players list')
            break
        match = lp_regex.match(line)
        if match is not None:
            (pid, name, pos_x, pos_y, pos_z, health, deaths, zombies, players, score,
             level, steamid, ip, ping) = match.groups()
            players_dict[int(pid)] = {
                'pid': int(pid),
                'name': name,
                'pos': (float(pos_x), float(pos_y), float(pos_z)),
                'health': int(health),
                'deaths': int(deaths),
                'zombies': int(zombies),
                'players': int(players),
                'score': int(score),
                'level': int(level),
                'steamid': steamid,
                'ip': ip,
                'ping': int(ping)
            }
    return players_dict
