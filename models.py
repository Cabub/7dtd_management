from datetime import datetime


class Player:

    def __init__(self, pid, name='', pos=(0.0, 0.0, 0.0), position_history=[], health=0, deaths=0, zombies=0,
                 players=0, score=0, level=0, steamid=None, ip=None, ping=99999, session_history=[], **kwargs):
        self.pid = pid
        self.name = name
        self.pos = pos
        self.position_history = position_history if position_history is not [] else [(pos, datetime.now())]
        self.health = health
        self.deaths = deaths
        self.zombies = zombies
        self.players = players
        self.score = score
        self.level = level
        self.steamid = steamid
        self.ip = ip
        self.ping = ping
        self.session_history = session_history

    def update(self, name=None, pos=None, health=None, deaths=None, zombies=None,
               players=None, score=None, level=None, ip=None, ping=None, **kwargs):
        if name is not None:
            self.name = name
        if pos is not None:
            self.pos = pos
            self.position_history.append((pos, datetime.now()))
        if health is not None:
            self.health = health
        if deaths is not None:
            self.deaths = deaths
        if zombies is not None:
            self.zombies = zombies
        if players is not None:
            self.players = players
        if score is not None:
            self.score = score
        if level is not None:
            self.level = level
        if ip is not None:
            self.ip = ip
        if ping is not None:
            self.ping = ping
        if name is not None:
            self.name = name

    def log_in(self):
        self.session_history.append((datetime.now(), None))

    def log_out(self):
        self.session_history[-1] = (self.session_history[-1][0], datetime.now())

    @property
    def playtime(self):
        return sum(map(lambda x: ((x[1] if x[1] else datetime.now()) - x[0]).total_seconds(), self.session_history))

    @property
    def logged_in(self):
        if len(self.session_history) == 0:
            return False
        return self.session_history[-1][1] is None

