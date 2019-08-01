import requests
import xml.etree.ElementTree as ET
import sys
import threading
import math
from time import sleep
import vlc

global sudo
sudo = True
global debug
debug = True
global playstatus
playstatus = "stopped"
global time
time = 0

global sudoplaystatus
sudoplaystatus = "stopped"
global sudotime
sudotime = 0
global sudolist
global time_changed
time_changed = False
global status_changed
status_changed = False

session = requests.Session()
info = "null"
global lag
lag = 0.1

def select_sudo():
    global sudo
    print(f"1. Alıcı\n2. Verici\nSeçimin: ")
    selection = input()
    if selection == "1":
        sudo = False
    if selection == "2":
        sudo = True

def log_auth():
    session.auth = ('', 'kalemkalem')

def get_info():
    threading.Timer(lag, get_info).start()
    info = session.get('http://127.0.0.1:8080/requests/status.xml', verify=False)
    tree = ET.fromstring(info.content)
    #tree = ET.parse(info)
    #root = tree.getroot()
    time = int(tree[5].text)
    playstatus = tree[12].text
    if debug:
        print(f" Zaman: {str(time)} Oynatma Durumu: {playstatus}")

def is_active(playstatus):
    global playtime
    if playstatus in ["stopped", "playing", "paused"]:
        return True
    else:
        return False

def send_server_info(time1, playstatus1, command):
        global debug
        #command veri akışını kesmek vs için kullanılabilir.
        #threading.Timer(0.4, send_server_info(time, playstatus, "nocommand")).start()
        url = "http://kurumuz.pythonanywhere.com/login/"

        client = requests.session()
        client.get(url, timeout=5)
        csrftoken = client.cookies['csrftoken']
        username = f'{str(sudo)};{playstatus1};{str(time1)};{command}'
        login_data = {'username': username, 'password': 'blabla', 'csrfmiddlewaretoken':csrftoken}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = client.post(url, data=login_data, timeout=5)
        if debug:
            print(username)
            print(response)
    #sudo;running;time;deletecommand

def get_server_sudo_info():
    global sudoplaystatus
    global sudotime
    global sudolist

    r = requests.get('http://kurumuz.pythonanywhere.com/sudo/')
    sudolist = r.text
    sudolist = sudolist.split("\n")
    #print(sudolist[0].split(';')[2])
    sudoplaystatus = sudolist[0].split(';')[1]
    sudotime = int(sudolist[0].split(';')[2])

def not_sudo_sync():
    global playstatus
    global time
    global sudoplaystatus
    global sudotime
    global status_changed
    global time_changed

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
    global sudolist
    global status_changed
    global playstatus

    if sudolist[0].split(';')[1] != playstatus:
        status_changed = True
    else:
        status_changed = False
    #if sudolist[0].split(';')[1] != sudolist[1].split(';')[1]:
        #status_changed = True
    #else:
    #    status_changed = False

def is_time_changed():
    global sudotime
    global time
    global time_changed
    print(f"timefark: {abs(sudotime-time)}")
    if abs(sudotime-time) > 5:
        time_changed = True
    else:
        time_changed = False


log_auth()
select_sudo()
get_info()


if sudo:

    while 1:

        if (playstatus == "false"): #stopped, playing, paused
            print("Oynayan içerik yok, lütfen bir içerik başlatın.")

        if (playstatus != "false"):
            #while 1:
            send_server_info(time, playstatus, "nocommand")
            

        if (playstatus not in ["false", "stopped", "playing", "paused"]):
            print("video kapatıldı.")

        sleep(lag)

if not sudo:

    while 1:

        if playstatus == "false":
            print("Oynayan içerik yok, karşı taraf bir içerik oynatmalı.")

        if playstatus != "false":
            get_server_sudo_info()
            #print("1")
            is_status_changed()
            #print("2")
            is_time_changed()
            #print("3")
            not_sudo_sync()
            #print("4")


        if (playstatus not in ["false", "stopped", "playing", "paused"]):
            print("video kapatıldı.")

        sleep(lag)



#if sudo == False:
    #while is_playing == "playing":
