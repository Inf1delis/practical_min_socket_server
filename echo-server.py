#!/usr/bin/env python3

import redis
# import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import os

hostName = ''
hostPort = 65432

# prefix = os.environ['PREFIX'] + ':'
prefix = 'lol'

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

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself

        try:
            json_data = json.loads(post_data)
            # sendMsg(conn, 'data received: '+json_data)
            action = server_action(json_data['action'])

            if action is None or json_data['action'] is "put" \
                              or json_data['action'] is "delete":
                self.send_response(400)
                self.wfile.write(bytes('{'+f'"status": "Bad Request"'+'}', "utf-8"))
                return

            status = action(json_data)

            self.send_response(200)
            self.wfile.write(bytes(
                '{'+f'"status": "{status[0]}","message": {status[1]}'+'}'.replace('\"', '"').replace("'",'"')), "utf-8")

        except:
            self.send_response(500)
            self.wfile.write(bytes('{'+f'"status": "Internal Server Error"'+'}', "utf-8"))


    def do_POST(self):
        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself

        # print(post_data)

        try:
            json_data = json.loads(post_data)
            # sendMsg(conn, 'data received: '+json_data)
            action = server_action(json_data['action'])

            # print(json_data)

            if action is None:
                self.send_response(400)
                self.wfile.write(bytes('{'+f'"status": "Bad Request"'+'}', "utf-8"))
                return

            # print("put")

            status = action(json_data)

            self.send_response(200)
            if isinstance(status, tuple):
                self.wfile.write(('{'+f'"status": "{status[0]}","message": {status[1]}'+'}')
                    .replace('\"', '"')
                    .replace("'",'"')
                    .encode("utf-8"))
            else:
                self.wfile.write(bytes('{'+f'"status": "{status}"'+'}', "utf-8"))

        except:
            self.send_response(500)
            self.wfile.write(bytes('{'+f'"status": "Internal Server Error"'+'}', "utf-8"))


    def do_DELETE(self):
        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself

        try:
            json_data = json.loads(post_data)
            # sendMsg(conn, 'data received: '+json_data)
            action = server_action(json_data['action'])

            if action is None or json_data['action'] is "get" \
                              or json_data['action'] is "put":
                self.send_response(400)
                self.wfile.write(bytes('{'+f'"status": "Bad Request"'+'}', "utf-8"))
                return

            status = action(json_data)

            self.send_response(200)
            self.wfile.write(bytes('{'+f'"status": "{status}"'+'}', "utf-8"))


        except:
            self.send_response(500)
            self.wfile.write(bytes('{'+f'"status": "Internal Server Error"'+'}', "utf-8"))




myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))

    # with conn:
    #     while True:
    #         try:
    #             data = conn.recv(1024)
    #             json_data = json.loads(data)
    #             # sendMsg(conn, 'data received: '+json_data)
    #             action = server_action(json_data['action'])

    #             if action is None:
    #                 sendMsg(conn, 'Bad Request')
    #                 continue

    #             status = action(json_data)

    #             if isinstance(status, tuple):
    #                 sendMsg(conn, ('{'+f'"status": "{status[0]}","message": {status[1]}'+'}').replace('\"', '"').replace("'",'"'))
    #             else:
    #                 sendMsg(conn, json.dumps({
    #                     "status": status
    #                     }))
    #         except:
    #             sendMsg(conn, json.dumps({
    #                     "status": "Internal Server Error"
    #                     }))














