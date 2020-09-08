import requests
import xml.etree.ElementTree as ET
import sys
import threading
import math
from time import sleep
import vlc
import db
import kodi
import websockets
import asyncio

mastertime = 0
masterps = "stopped" #master playstatus
time_changed = False
status_changed = False
player_name = "vlc"
session = requests.Session()
masterlist = []
lag = 0.1

def select_player():
    global player_name
    print(f"1. vlc\n2. Kodi\nSeçim: ")
    players = input()
    if players == "1":
        player_name = "vlc"
    if players == "2":
        player_name = "kodi"
        
def select_master():
    print(f"1. Alıcı\n2. Verici\nSeçimin: ")
    selection = input()
    if selection == "1":
        db.master = False
    if selection == "2":
        db.master = True

async def send_server_info_ws(websocket, path):
    command = "no"
    message = f'{str(db.master)};{db.ps};{str(db.time)};{command}'
    await websocket.send(message)

class Server:
    url = "None"
    username = ""

    def set_url(self, new_url):
        self.url = new_url

    async def get_server_info_ws(self):
        global mastertime
        global masterps
        global masterlist

        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            message = await websocket.recv()
            masterlist = message.split("\n")
            masterps = masterlist[0].split(';')[1]
            mastertime = int(masterlist[0].split(';')[2])
            #master;running;time;deletecommand   

class Player:
    name = "None"

    def log_auth(self, password):
        session.auth = ('', password)

    def set_player(self, new_name):
        self.name = new_name

    def play(self):
        if self.name == "vlc":
            vlc.play()
        if self.name == "kodi":
            kodi.play()
            return
        if self.name == "mpv":
            return

    def stop(self):
        if self.name == "vlc":
            vlc.stop()
        if self.name == "kodi":
            kodi.stop()
            return
        if self.name == "mpv":
            return      

    def pause(self):
        if self.name == "vlc":
            vlc.pause()
        if self.name == "kodi":
            kodi.pause()
            return
        if self.name == "mpv":
            return

    def seek(self, time):
        if self.name == "vlc":
            print("seek")
            vlc.seek(time)
        if self.name == "kodi":
            print("seek")
            kodi.seek(time)
            return
        if self.name == "mpv":
            return

    def get_info(self):
        if self.name == "vlc":
            vlc.get_info()
        if self.name == "kodi":
            kodi.get_info()
            return
        if self.name == "mpv":
            return    

    def client_sync(self):
        global status_changed
        global masterps
        global time_changed
        if status_changed:
            if masterps == "stopped":
                self.stop()
                print("Oynatma bitirildi.")
            if masterps == "paused":
                self.pause()
                print("Oynatma duraklatıldı.")
            if masterps == "playing":
                self.play()
                print("Oynatma başlatıldı.")

        if time_changed:
            self.seek(mastertime)

    def is_status_changed(self):
        global masterps
        global status_changed
        if masterps != db.ps:
            status_changed = True
        else:
            status_changed = False

    def is_time_changed(self):
        global mastertime
        global time_changed
        #print(f"timefark: {abs(mastertime-db.time)}")
        if abs(mastertime-db.time) > 3:
            time_changed = True
        else:
            time_changed = False

    def is_active(self, ps):
        if ps in ["stopped", "playing", "paused"]:
            return True
        else:
            return False

server = Server()
server.set_url("http://kurumuz.pythonanywhere.com")
player = Player()
player.log_auth("kalemkalem")
select_player()
player.set_player(player_name)
select_master()
player.get_info()


if db.master:

    start_server = websockets.serve(send_server_info_ws, "localhost", 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    
    while 1:

        if (db.ps == "false"): #stopped, playing, paused
            print("Oynayan içerik yok, lütfen bir içerik başlatın.")

        if (db.ps not in ["false", "stopped", "playing", "paused"]):
            print("video kapatıldı.")

        sleep(lag)

if not db.master:

    while 1:

        if db.ps == "false":
            print("Oynayan içerik yok, karşı taraf bir içerik oynatmalı.")

        if db.ps != "false":
            asyncio.get_event_loop().run_until_complete(server.get_server_info_ws())
            player.is_status_changed()
            player.is_time_changed()
            player.client_sync()

        if (db.ps not in ["false", "stopped", "playing", "paused"]):
            print("video kapatıldı.")

        sleep(lag)
