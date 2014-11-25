#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import config
import vk_auth
import sys
import json
import urllib2
from urllib import urlencode
import csv
import datetime
import time
import re
import os
from antigate import AntiGate

def call_api(method, params, token):
    params.append(('access_token', token))
    url = 'https://api.vk.com/method/%s?%s' % (method, urlencode(params))
    time.sleep(0.3)
    return json.loads(urllib2.urlopen(url).read())

def call_api_notoken(method, params):
    url = 'https://api.vk.com/method/%s?%s' % (method, urlencode(params))
    time.sleep(0.3)
    return json.loads(urllib2.urlopen(url).read())

def find_song_name(record):
    record = re.sub(r'%20', ' ', record)
    record = re.sub(r'.mp3', '', record)
    record = re.sub(r'[^\w,-\\ ]', '', record)
    record = record.split('\\')[-1]
    print record
    return record

def process_song(song):
    params = [('q', song), ('auto_complete', '1'), ('sort', '2')]
    response = call_api('audio.search', params , gnz['token'])
    if 'error' in response:
        response = error_happens(response, song, gnz, params)

    if 'response' in response:
        response = response['response']
        if response[0] > 0:
            response = response[1]
            #На этом моменте мы выбрали одну единственную песню 
            artist = ''
            if 'aid' in response:
                aid = response['aid']
                owner_id = response['owner_id']
                for current in [ubz, rfm, kpr]:
                    zaparams = [('audio_id', aid), ('owner_id', owner_id), ('group_id', current['group_id'])]
                    resp_audio = call_api('audio.add', zaparams, current['token'])
                    if 'error' in resp_audio:
                        error_happens(resp_audio, song, current, zaparams)
                
                    if 'response' in resp_audio: 
                        print "Audio ", song, "aded!"
                        resp_audio = resp_audio['response']
                        if 'title' in response:
                            title = response['title']
                        resp_a = call_api('audio.edit', [('owner_id', -int(current['group_id'])), ('title',  title.encode('UTF-8') + ' | Time Club' ), ('audio_id', resp_audio)], current['token'])


                for current in [gnz, ubz, rfm, kpr]:
                    ppzarams = [('audio_id', aid), ('owner_id', owner_id)]
                    resp_audio = call_api('audio.add', ppzarams, current['token'])
                    if 'error' in resp_audio:
                        error_happens(resp_audio, song, current, ppzarams)
                        
                    if 'response' in resp_audio: 
                        print "Audio ", song, "aded!"
                        resp_audio = resp_audio['response']
                        if 'title' in response:
                            title = response['title']
                        resp_a = call_api('audio.edit', [('owner_id', int(current['user_id'])), ('title',  title.encode('UTF-8') + ' | Time Club' ), ('audio_id', resp_audio)], current['token'])
        else:
            errors.write('%s\n' %song)


def error_happens(response, song, current, params):
    print "===================ERROR=============================="
    print response
    print "===================ERROR END=========================="
    response = response['error']
    if response['error_code'] == 14: #Captcha needed
        os.popen("curl '%s' > captcha1.jpg" %response['captcha_img'])
        gate = AntiGate(config.ANTICAPCHA_KEY, auto_run=False)
        captcha1 = gate.send('captcha1.jpg')
        captcha =  gate.get(captcha1)

        # print captcha
        # print "Введи капчу!"
        # captcha = sys.stdin.readline()
        # captcha = captcha.split('\n')[0]
        
        params += [('captcha_sid', response['captcha_sid']), ('captcha_key', captcha)]
        method = ''
        for para in response['request_params']:
            if para['key'] == 'method':
                method = para['value']
            else:
                pass
            
        print params, '========', method
        r = call_api(method, params, current['token'])
        return r
    else:
        print "Дело не в капче!\n", response['error_msg']
        return 


errors = open('./errors.txt', 'w')

for current in config.clubs:
    current['token'], user_id = vk_auth.auth(current['email'], current['password'], config.client_id, "audio")
    print "done!"
# # Если тут всплыло "raise RuntimeError("Expected success here")" скорее всего всплыла капча, апи не умеет это обрабатывать

records = open('./songs.txt', 'r')

for record in records:
    song = find_song_name(record)
    process_song(song)
    print '======================================='
errors.close()