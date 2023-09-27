# mostly used as reference point to build your own flask app.

import json
from flask import request, Blueprint
from satorirendezvous.server.rest.behaviors import ClientConnect
from satorirendezvous.server.rest.constants import rendezvousPort

rendezvousApp = Blueprint('rendezvous', __name__)
conn = ClientConnect(fullyConnected=True)


@rendezvousApp.route('/', methods=['GET'])
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


@rendezvousApp.route('/api/v0/raw/<ip>', methods=['POST'])
def raw(ip=None):
    ''' accept a raw message from the client '''
    # logging.debug(request.get_data())
    if request.content_length is None:
        return "Request payload missing", 400
    if request.content_length > 10 * 1024:  # 10 kb or 0.01024 MB
        return "Request payload is too large", 413
    return json.dumps({'response': conn.router(request.get_data(), (ip, rendezvousPort))}), 200
