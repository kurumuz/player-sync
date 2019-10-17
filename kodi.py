from kodijson import Kodi, PLAYER_VIDEO
kodi = Kodi("http://192.168.1.26:8080/jsonrpc")
import json
import threading
import db
import datetime

ctype = "null"
item = "null"

#stopped, playing, paused
def get_info():
    threading.Timer(0.1, get_info).start()
    info = kodi.Player.GetActivePlayers()
    #print(info)
    if info['result'] == []:
        db.ps = "stopped"
        return
    else:
        db.playerid = info['result'][0]['playerid']
        ctype = info['result'][0]['type']

    #print(kodi.Player.GetItem(playerid=playerid, properties=['thumbnail']))
    #print(kodi.Player.GetItem(playerid=playerid, properties=['file']))
    #time2 = {'time': {'hours': 0, 'milliseconds': 165, 'minutes': 25, 'seconds': 42}}
    db.time = kodi.Player.GetProperties(playerid=db.playerid, properties=['time'])['result']['time']
    db.time = db.time["hours"]*60*60 + db.time["minutes"]*60 + db.time["seconds"]
    state = kodi.Player.GetProperties(playerid=db.playerid, properties=['speed'])['result']['speed']
    if state == 1:
        db.ps = "playing"
    if state == 0:
        db.ps = "paused"

    if db.debug:
        print(f" Zaman: {str(db.time)} Oynatma Durumu: {db.ps}")


def pause():
    kodi.Player.PlayPause(playerid=db.playerid, play=False)
    return

def play():
    kodi.Player.PlayPause(playerid=db.playerid, play=True)
    return

def stop():
    kodi.Player.Stop(playerid=db.playerid)
    return

def seek(time):

    time3 = str(datetime.timedelta(seconds=time)).split(':')
    time2 = {'time': {'hours': int(time3[0]), 'milliseconds': 1, 'minutes': int(time3[1]), 'seconds': int(time3[2])}}
    kodi.Player.Seek(playerid=db.playerid, value=time2)
    return
