#!/usr/bin/env python3

import redis
import socket
import json
import os

HOST = ''
PORT = 65432

prefix = os.environ['PREFIX'] + ':'
# prefix = 'lol'

def sendMsg(conn, message):
    message += '\n'
    conn.sendall(message.encode('utf-8'))

def get(json_data):
    key = json_data['key']
    cache = redis.Redis(host='rediska', port=6379)
    cache.ping()
    byte_data = cache.get(key)
    if byte_data is None:
        return "Not Found"
    value = ''.join(map(chr, byte_data))
    # value = cache.get(key).decode('utf-8')

    return ('Ok', value)

def put(json_data):
    key = json_data['key']
    try:
        value = json.dumps(json_data['message'])
    except:
        value = json_data['message']
    cache = redis.Redis(host='rediska', port=6379)
    cache.ping()

    if cache.get(key) is not None:
        cache.set(key, value)
        return "Ok"
    else:
        cache.set(key, value)
        return "Created"

def delete(json_data):
    key = json_data['key']
    cache = redis.Redis(host='rediska', port=6379)
    cache.ping()
    if cache.exists(key):
        cache.delete(key)
        return "Ok"
    else:
        return "Not Found"

def server_action(str):
    actions = {
        "get":get,
        "put":put,
        "delete":delete
    }
    try:
        return actions[str]
    except:
        return None

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                json_data = json.loads(data)
                # sendMsg(conn, 'data received: '+json_data)
                action = server_action(json_data['action'])

                if action is None:
                    sendMsg(conn, 'Bad Request')
                    continue

                status = action(json_data)

                if isinstance(status, tuple):
                    sendMsg(conn, ('{'+f'"status": "{status[0]}","message": {status[1]}'+'}').replace('\"', '"').replace("'",'"'))
                else:
                    sendMsg(conn, json.dumps({
                        "status": status
                        }))
            except:
                sendMsg(conn, json.dumps({
                        "status": "Internal Server Error"
                        }))














