import requests
import threading
import xml.etree.ElementTree as ET
import db

session = requests.Session()
session.auth = ('', 'kalemkalem')

def get_info():
    threading.Timer(0.1, get_info).start()
    info = session.get('http://127.0.0.1:8080/requests/status.xml', verify=False)
    tree = ET.fromstring(info.content)
    db.time = int(tree[5].text)
    db.playstatus = tree[12].text
    if db.debug:
        print(f" Zaman: {str(db.time)} Oynatma Durumu: {db.playstatus}")

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