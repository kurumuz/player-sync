import requests
import xml.etree.ElementTree as ET
import sys
import threading
import math
from time import sleep
import vlc
import db

sudoplaystatus = "stopped"
sudotime = 0
time_changed = False
status_changed = False

session = requests.Session()
infolist = []
lag = 0.1

def select_sudo():
    print(f"1. Alıcı\n2. Verici\nSeçimin: ")
    selection = input()
    if selection == "1":
        db.sudo = False
    if selection == "2":
        db.sudo = True

def log_auth():
    session.auth = ('', 'kalemkalem')

def is_active(playstatus):
    if playstatus in ["stopped", "playing", "paused"]:
        return True
    else:
        return False

def send_server_info(time1, playstatus1, command):
        #command veri akışını kesmek vs için kullanılabilir.
        #threading.Timer(0.4, send_server_info(time, playstatus, "nocommand")).start()
        url = "http://kurumuz.pythonanywhere.com/login/"

        client = requests.session()
        client.get(url, timeout=5)
        csrftoken = client.cookies['csrftoken']
        username = f'{str(db.sudo)};{playstatus1};{str(time1)};{command}'
        login_data = {'username': username, 'password': 'blabla', 'csrfmiddlewaretoken':csrftoken}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = client.post(url, data=login_data, timeout=5)
        if db.debug:
            print(username)
            print(response)
    #sudo;running;time;deletecommand

def get_server_sudo_info():
    r = requests.get('http://kurumuz.pythonanywhere.com/sudo/')
    sudolist = r.text
    sudolist = sudolist.split("\n")
    #print(sudolist[0].split(';')[2])
    sudoplaystatus = sudolist[0].split(';')[1]
    sudotime = int(sudolist[0].split(';')[2])

def not_sudo_sync():

    if status_changed:
        if sudoplaystatus == "stopped":
            vlc.stop()
            print("Oynatma bitirildi.")
        if sudoplaystatus == "paused":
            vlc.pause()
            print("Oynatma duraklatıldı.")
        if sudoplaystatus == "playing":
            vlc.play()
            print("Oynatma başlatıldı.")
    print(time_changed)

    if time_changed:
        vlc.seek(sudotime)

def is_status_changed():

    if sudolist[0].split(';')[1] != db.playstatus:
        status_changed = True
    else:
        status_changed = False

def is_time_changed():

    print(f"timefark: {abs(sudotime-db.time)}")
    if abs(sudotime-db.time) > 5:
        time_changed = True
    else:
        time_changed = False


log_auth()
select_sudo()
vlc.get_info()


if db.sudo:

    while 1:

        if (db.playstatus == "false"): #stopped, playing, paused
            print("Oynayan içerik yok, lütfen bir içerik başlatın.")

        if (db.playstatus != "false"):
            #while 1:
            send_server_info(db.time, db.playstatus, "nocommand")
            

        if (db.playstatus not in ["false", "stopped", "playing", "paused"]):
            print("video kapatıldı.")

        sleep(lag)

if not db.sudo:

    while 1:

        if db.playstatus == "false":
            print("Oynayan içerik yok, karşı taraf bir içerik oynatmalı.")

        if db.playstatus != "false":
            get_server_sudo_info()
            is_status_changed()
            is_time_changed()
            not_sudo_sync()

        if (db.playstatus not in ["false", "stopped", "playing", "paused"]):
            print("video kapatıldı.")

        sleep(lag)