from console import Console
import commands
import time
from config import config
import database
from models import Player


def debug_console():
    with Console(config['ip'], config['port']) as console:
        console.log_in(config['secret'])
        while True:
            cmd = input('>')
            if cmd != 'logs':
                console.flush_log()
                console.send_command(cmd)
            if cmd == 'exit':
                break
            time.sleep(.5)
            for log in console.flush_log():
                print(log)


def track_players():
    if config['debug']: print('loading')
    try:
        player_states = database.load()
    except FileNotFoundError as e:
        player_states = dict()
    while True:
        if config['debug']: print('connecting to', config['ip'], config['port'])
        with Console(config['ip'], config['port']) as console:
            try:
                console.log_in(config['secret'])
                if config['debug']: print('logged in')
                players = commands.player_list(console)
                state_changed = False
                for pid, player in player_states.items():
                    if player.pid in players:
                        if not player.logged_in:
                            if config['debug']: print('{} logged in'.format(player.name))
                            player.log_in()
                        if config['debug']: print('updating {}'.format(player.name))
                        player_states[player.pid].update(**players[pid])
                        del players[player.pid]
                        state_changed = True
                    elif player.logged_in:
                        if config['debug']: print('{} logged out'.format(player.name))
                        player.log_out()
                        state_changed = True
                for pid, player_dict in players.items():
                    if config['debug']: print('creating {}'.format(player_dict['name']))
                    player = Player(**player_dict)
                    player.log_in()
                    player_states[pid] = player
                    state_changed = True
                if config['debug']: print('saving')
                if state_changed:
                    database.save(player_states)
                time.sleep(config['poll_interval'])
            except KeyboardInterrupt as e:
                if config['debug']: print('exiting')
                database.save(player_states)
                break


def __main__(*args):
    #debug_console()
    track_players()


if __name__ == '__main__':
    __main__()