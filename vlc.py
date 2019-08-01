import requests
import threading

session = requests.Session()
session.auth = ('', 'kalemkalem')


def pause():
    r = session.get('http://127.0.0.1:8080/requests/status.xml?command=pl_pause', verify=False)
    return

def play():
    r = session.get('http://127.0.0.1:8080/requests/status.xml?command=pl_play', verify=False)
    return

def stop():
    r = session.get('http://127.0.0.1:8080/requests/status.xml?command=pl_stop', verify=False)
    return

def seek(time):
    r = session.get('http://127.0.0.1:8080/requests/status.xml?command=seek&val=' + str(time) , verify=False)
    return