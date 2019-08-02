import requests
import xml.etree.ElementTree as ET
import sys
import threading
import math
from time import sleep
import vlc
import db
import kodi

mastertime = 0
masterps = "stopped" #master playstatus
time_changed = False
status_changed = False
player_name = "kodi"
session = requests.Session()
masterlist = []
lag = 0.1

def select_master():
    print(f"1. Alıcı\n2. Verici\nSeçimin: ")
    selection = input()
    if selection == "1":
        db.master = False
    if selection == "2":
        db.master = True

class Server:
    url = "None"
    username = ""

    def set_url(self, new_url):
        self.url = new_url

    def send_server_info(self, time1, playstatus1, command):
            loginurl = f"{self.url}/login/"
            client = requests.session()
            client.get(loginurl, timeout=5)
            csrftoken = client.cookies['csrftoken']
            username2 = self.username
            self.username = f'{str(db.master)};{playstatus1};{str(time1)};{command}'

            if self.username != username2: #possible optimization, needs testing.
                login_data = {'username': self.username, 'password': 'blabla', 'csrfmiddlewaretoken':csrftoken}
                response = client.post(loginurl, data=login_data, timeout=5)
                if db.debug:
                    print(self.username)
                    print(response)
        #master;running;time;deletecommand   

    def get_server_info(self):
        global mastertime
        global masterps
        global masterlist

        r = requests.get(f'{self.url}/sudo/')
        masterlist = r.text
        masterlist = masterlist.split("\n")
        masterps = masterlist[0].split(';')[1]

         #print(f"mastertime {mastertime}")
        mastertime = int(masterlist[0].split(';')[2])
class Player:
    name = "None"

    def log_auth(self, password):
        session.auth = ('', password)

    def set_player(self, new_name):
        self.name = new_name

    def play(self):kimsn senwho are you
        if self.name == "vlc":
            vlc.play()kimsn senwho are you
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
player.set_player(player_name)
select_master()
player.get_info()


if db.master:

    while 1:

        if (db.ps == "false"): #stopped, playing, paused
            print("Oynayan içerik yok, lütfen bir içerik başlatın.")

        if (db.ps != "false"):
            #while 1:
            server.send_server_info(db.time, db.ps, "nocommand")
            

        if (db.ps not in ["false", "stopped", "playing", "paused"]):
            print("video kapatıldı.")

        sleep(lag)

if not db.master:

    while 1:

        if db.ps == "false":
            print("Oynayan içerik yok, karşı taraf bir içerik oynatmalı.")

        if db.ps != "false":
            server.get_server_info()
            player.is_status_changed()
            player.is_time_changed()
            player.client_sync()

        if (db.ps not in ["false", "stopped", "playing", "paused"]):
            print("video kapatıldı.")

        sleep(lag)