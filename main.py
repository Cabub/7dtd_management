from console import Console
import time
import yaml
import os


path = __file__
if path.endswith('.pyc') and os.path.exists(path[:-1]):
    path = path[:-1]

path = os.path.realpath(path)

with open(os.path.join(os.path.dirname(path), 'config.yaml')) as fs:
    config = yaml.load(fs)

with Console(config['ip'], config['port']) as console:
    console.log_in(config['secret'])
    cmd = ''
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