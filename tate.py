import json
import requests
i=1
while 25>i: 
    print(i)
    r= requests.get(f"https://mightyanimeapi.cf/video/tate-no-yuusha-no-nariagari-{i}-bolum")
    r_dict = json.loads(r.text)
    a = 0
    try:
        while 20 > a:
            o = 0
            while 20 > o:
                number = r_dict['msg'][o]['alternatives'][a]['name']
                if number == "DAILYMOTION":
                    print(f"http://www.dailymotion.com/video/{r_dict['msg'][0]['alternatives'][a]['url'].split('/')[5]}")
                    break
                o = o + 1
            a = a + 1
    except:
        print("hata")    
    #print(number)
    #print(f"http://www.dailymotion.com/video/{number}")

    i = i + 1
