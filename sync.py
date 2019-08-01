import requests
import xml.etree.ElementTree as ET
import sys
import threading
import math
from time import sleep
import vlc
import db

sudotime = 0
sudoplaystatus = "stopped"
sudotime = 0
time_changed = False
status_changed = False
player_name = "vlc"
session = requests.Session()
sudolist = []
lag = 0.1

def select_sudo():
    print(f"1. Alıcı\n2. Verici\nSeçimin: ")
    selection = input()
    if selection == "1":
        db.sudo = False
    if selection == "2":
        db.sudo = True

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
            self.username = f'{str(db.sudo)};{playstatus1};{str(time1)};{command}'

            if self.username != username2: #possible optimization, needs testing.
                login_data = {'username': self.username, 'password': 'blabla', 'csrfmiddlewaretoken':csrftoken}
                response = client.post(loginurl, data=login_data, timeout=5)
                if db.debug:
                    print(self.username)
                    print(response)
        #sudo;running;time;deletecommand   

    def get_server_info(self):
        global sudotime
        global sudoplaystatus
        global sudolist

        r = requests.get(f'{self.url}/sudo/')
        sudolist = r.text
        sudolist = sudolist.split("\n")
        sudoplaystatus = sudolist[0].split(';')[1]

        print(f"sudotime {sudotime}")
        sudotime = int(sudolist[0].split(';')[2])



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
            return
        if self.name == "mpv":
            return

    def stop(self):
        if self.name == "vlc":
            vlc.stop()
        if self.name == "kodi":
            return
        if self.name == "mpv":
            return      

    def pause(self):
        if self.name == "vlc":
            vlc.pause()
        if self.name == "kodi":
            return
        if self.name == "mpv":
            return

    def seek(self, time):
        if self.name == "vlc":
            print("seek")
            vlc.seek(time)
        if self.name == "kodi":
            return
        if self.name == "mpv":
            return

    def get_info(self):
        if self.name == "vlc":
            vlc.get_info()
        if self.name == "kodi":
            return
        if self.name == "mpv":
            return    

    def client_sync(self):
        global status_changed
        global sudoplaystatus
        global time_changed
        if status_changed:
            if sudoplaystatus == "stopped":
                self.stop()
                print("Oynatma bitirildi.")
            if sudoplaystatus == "paused":
                self.pause()
                print("Oynatma duraklatıldı.")
            if sudoplaystatus == "playing":
                self.play()
                print("Oynatma başlatıldı.")

        if time_changed:
            self.seek(sudotime)

    def is_status_changed(self):
        global sudoplaystatus
        global status_changed
        if sudoplaystatus != db.playstatus:
            status_changed = True
        else:
            status_changed = False

    def is_time_changed(self):
        global sudotime
        global time_changed
        print(f"timefark: {abs(sudotime-db.time)}")
        if abs(sudotime-db.time) > 5:
            time_changed = True
        else:
            time_changed = False

    def is_active(self, playstatus):
        if playstatus in ["stopped", "playing", "paused"]:
            return True
        else:
            return False

server = Server()
server.set_url("http://kurumuz.pythonanywhere.com")
player = Player()
player.log_auth("kalemkalem")
player.set_player(player_name)
select_sudo()
player.get_info()


if db.sudo:

    while 1:

        if (db.playstatus == "false"): #stopped, playing, paused
            print("Oynayan içerik yok, lütfen bir içerik başlatın.")

        if (db.playstatus != "false"):
            #while 1:
            server.send_server_info(db.time, db.playstatus, "nocommand")
            

        if (db.playstatus not in ["false", "stopped", "playing", "paused"]):
            print("video kapatıldı.")

        sleep(lag)

if not db.sudo:

    while 1:

        if db.playstatus == "false":
            print("Oynayan içerik yok, karşı taraf bir içerik oynatmalı.")

        if db.playstatus != "false":
            server.get_server_info()
            player.is_status_changed()
            player.is_time_changed()
            player.client_sync()

        if (db.playstatus not in ["false", "stopped", "playing", "paused"]):
            print("video kapatıldı.")

        sleep(lag)