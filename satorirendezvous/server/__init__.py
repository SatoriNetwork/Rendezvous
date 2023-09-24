'''
Our original design was to keep persistent connections open between the 
rendezvous server and the client so we used a websocket approach (server.py).
however, we discovered that a persistent connection is not entirely necessary
for most applications, so we created this http RESTful approach (app.py).

in this design clients will check in periodically with the rendezvous server, 
authenticating themselves and asking for a list of peers. the rendezvous server
will provide the full list of peers each time.
'''
