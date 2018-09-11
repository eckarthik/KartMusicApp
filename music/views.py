# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mutagen import File
from mutagen.flac import FLAC
from django.shortcuts import render
import requests,urllib
from bs4 import BeautifulSoup
# Create your views here.
def index(request):
    return render(request,'music/index.html')

def showlinks(request):
    songs = {}
    search_text = urllib.quote(str(request.POST['song']))
    url = "http://hqzone.telugump3z.net/search.php?type=ffile&search="+search_text
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30."}
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, "html.parser")
    songs_counter = 0
    for bg in soup.find_all("div",{"class":"bg"}):
        song = bg.find("span", {"class": "yt_list_title"})
        song_link = song.a.get("href")
        song_title = song.a.text
        req2 = requests.get(song_link, headers=headers)
        soup2 = BeautifulSoup(req2.text, "html.parser")
        #getting song details
        song_details = ''
        song_details_tag = soup2.find("div",{"class":"menu"})
        detail_counter = 0 #dont show more than 3 details
        for detail in song_details_tag.find_all("a"):
            if detail_counter>=2:
                break
            else:
                song_details = song_details+"<br/>"+detail.text
            detail_counter = detail_counter+1
        #end getting song details
        songs[songs_counter] = {'song_title': song_title, 'song_links': '','song_details':song_details}
        quality_songs_counter = 0
        quality_songs = {}
        for song_quality in soup2.find_all("div", {"class": "d2", "align": "left"}):
            try:
                action = song_quality.find("form").get("action")
                dir = song_quality.find("input", {"name": "dir"}).get("value")
                file = song_quality.find("input", {"name": "file"}).get("value")
                cat = song_quality.find("input", {"name": "cat"}).get("value")
                quality = song_quality.find("input", {"class": "submit"}).get("value")
            except AttributeError:
                print "None"
            else:
                post_data = {"dir": dir, "file": file, "cat": cat,"action":action,"quality":quality,"song_link":song_link}
                quality_songs[quality_songs_counter] = post_data
            quality_songs_counter = quality_songs_counter+1
        songs[songs_counter]['song_links'] = quality_songs
        songs_counter = songs_counter + 1
    print songs
    return render(request,"music/showsongs.html",context={'songs':songs})

def fetchfile(request):
    action = request.POST['action']
    dir = request.POST['dir']
    file = request.POST['file']
    cat = request.POST['cat']
    song_link = request.POST['song_link']
    quality = request.POST['quality']
    post_url = "http://hqzone.telugump3z.net/" + str(action)
    post_data = {"dir": dir, "file": file, "cat": cat}
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30.",
        "Referer": song_link}
    req3 = requests.post(post_url, headers=headers, data=post_data)
    flac_tags = {}
    #For cat = m4a (Lossless)
    if cat=="itune":
        with open('songs/' + cat + '.m4a', 'wb') as h:
            for block in req3.iter_content(1024):
                h.write(block)
        fname = "songs/" + cat + ".m4a"
        file = File(fname)  # mutagen can automatically detect format and type of tags
        artwork = file.tags['covr'][0]  # access APIC frame and grab the image
        with open("songs/albumart" + cat + ".jpg", 'wb') as img:
            img.write(artwork)  # write artwork to new image
    elif cat=="flac":
        with open('songs/' + cat + '.flac', 'wb') as h:
            for block in req3.iter_content(1024):
                h.write(block)
        fname = "songs/" + cat + ".flac"
        file = FLAC(fname)  # mutagen can automatically detect format and type of tags
        for p in file.pictures:
            with open("songs/albumart" + cat + ".jpg", 'wb') as img:
                img.write(p.data)  # write artwork to new image
        flac_tags = {'song_title':file.tags['TITLE'][0],'song_artist':file.tags['ARTIST'][0],'song_album':file.tags['ALBUM'][0]}
    else:
        with open('songs/'+cat + '.mp3', 'wb') as h:
            for block in req3.iter_content(1024):
                h.write(block)
        fname = "songs/"+cat+".mp3"
        file = File(fname)  # mutagen can automatically detect format and type of tags
        artwork = file.tags['APIC:'].data  # access APIC frame and grab the image
        with open("songs/albumart"+cat+".jpg", 'wb') as img:
            img.write(artwork)  # write artwork to new image
    '''f = open(fname, "rb")
    response = HttpResponse()
    response.write(f.read())
    response['Content-Type'] = 'audio/mp3'
    response['Content-Length'] = os.path.getsize(fname)
    return response'''
    return render(request,'music/player.html',{'filename':"/"+fname,'album_art_location':"/songs/albumart"+cat+".jpg",'flac_tags':flac_tags})

def player(request):
    return render(request,"music/player.html")
