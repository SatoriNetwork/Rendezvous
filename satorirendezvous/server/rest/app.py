#!/usr/bin/env python
# -*- coding: utf-8 -*-

# run with:
# sudo nohup /app/anaconda3/bin/python app.py > /dev/null 2>&1 &

import threading
import json
from flask import Flask, redirect, request, g
from waitress import serve
import secrets
import os
from satorilib import logging
from satorirendezvous.server.rest.behaviors import ClientConnect
logging.setup(file='/tmp/server.log', stdoutAndFile=True)
logging.info('starting satori website...')

###############################################################################
## Globals ####################################################################
###############################################################################

debug = True
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
DEVMODE = os.getenv('APPDATA') is not None
connLock = threading.Lock()

def getConn():
    if not hasattr(g, 'conn'):
        g.conn = ClientConnect(fullyConnected=True)
    return g.conn


def useConn(data: bytes, ip: str):
    conn = getConn()
    with connLock:
        return conn.router(data, (ip, 80))

###############################################################################
## Flask Hooks ################################################################
###############################################################################


@app.before_request
def before_request():
    if (
        not DEVMODE and
        request.url in [
            'https://satorinet.io', 'http://satorinet.io', 'satorinet.io', 'www.satorinet.io', 'https://www.satorinet.io', 'http://www.satorinet.io',
            'https://satorinet.io/', 'http://satorinet.io/', 'satorinet.io/', 'www.satorinet.io/', 'https://www.satorinet.io/', 'http://www.satorinet.io/'
        ] and not request.is_secure
    ):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

###############################################################################
## Errors #####################################################################
###############################################################################


@app.errorhandler(404)
def not_found(e):
    return '404', 404

###############################################################################
## Routes - Browser ###########################################################
###############################################################################


@app.route('/', methods=['GET'])
def home():
    ''' home page '''
    return (
        '<!DOCTYPE html>'
        '<html lang="en">'
        '<head>'
        '<meta charset="utf-8" />'
        '<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">'
        '<title>Satori Rendezvous Server</title>'
        '</head>'
        '<body>'
        '<h1>Welcome to the Satori Rendezvous Server!</h1>'
        '<p>Let your workings remain a mystery, just show people the results.</p>'
        '</body>'
        '</html>'), 200


###############################################################################
## Routes - API ###############################################################
###############################################################################

@app.route('/api/v0/raw/<ip>', methods=['POST'])
def raw(ip=None):
    ''' accept a raw message from the client '''
    # logging.debug(request.get_data())
    if request.content_length is None:
        return "Request payload missing", 400
    if request.content_length > 10 * 1024:  # 10 kb or 0.01024 MB
        return "Request payload is too large", 413
    return json.dumps({'response': useConn(request.get_data(), ip)}), 200

###############################################################################
## Entry ######################################################################
###############################################################################


if __name__ == '__main__':
    # serve(app, host='0.0.0.0', port=80)
    if DEVMODE:
        app.run(
            host='0.0.0.0',
            port=5002,
            threaded=True,
            debug=debug,
            use_reloader=False)  # fixes run twice issue
    else:
        certificateLocations = (
            '/etc/letsencrypt/live/satorinet.io/fullchain.pem',
            '/etc/letsencrypt/live/satorinet.io/privkey.pem')
        # app.run(host='0.0.0.0', port=80, threaded=True,
        #        ssl_context=certificateLocations)
        # app.run(host='0.0.0.0', port=5002, threaded=True, debug=debug)
        serve(app, host='0.0.0.0', port=80, url_scheme='https',)
        # gunicorn -c gunicorn.py.ini --certfile /etc/letsencrypt/live/satorinet.io/fullchain.pem --keyfile /etc/letsencrypt/live/satorinet.io/privkey.pem -b 0.0.0.0:443 app:app


# sudo nohup /app/anaconda3/bin/python app.py > /dev/null 2>&1 &
# > python satori\web\app.py


# python .\satoricentral\web\app.py
