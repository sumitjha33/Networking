# Mini Load Balancer (Built from Raw TCP Sockets)
A load balancer built from scratch in Python — no Flask, no nginx, no external libraries doing the heavy lifting. Just raw sockets, threading, and the actual HTTP protocol, because I wanted to understand what tools like nginx and HAProxy are really doing under the hood instead of just using them.

# What it does:
It sits in front of 3 backend servers and distributes incoming requests between them using round-robin rotation. If a backend goes down, it's automatically detected and removed from rotation — no manual intervention, no crash, no dropped requests to the servers still running.
Browser → Load Balancer (:8080) → Backend 1 / 2 / 3 (:5001-5003)

# Why I built it this way
Most "networking" student projects are chat apps. I wanted to build something closer to actual infrastructure — the kind of component that's genuinely running in production behind real websites. A load balancer forced me to actually understand:

- How TCP sockets work at a byte level (no framework hiding it from me)
- How to parse and construct raw HTTP requests/responses by hand
- Why a single recv() call doesn't guarantee you got the whole message (and how to handle that correctly)
- How a program can be a server and a client at the same time
- Real concurrency, using threads to handle multiple clients simultaneously
- What "health checking" and "failover" actually mean, by implementing them instead of reading about them

# Features
Round-robin routing — requests are distributed evenly across all healthy backends
Automatic health checks — a background thread checks every backend every few seconds
Failover — unhealthy backends are automatically skipped during rotation
Graceful degradation — if every backend is down, it responds with a proper 503 Service Unavailable instead of hanging or crashing
Concurrent request handling — each client is handled on its own thread, so one slow request doesn't block everyone else

# How to run it
You'll need Python 3 and Flask installed for the backend servers:

bash
pip install flask

Open 4 terminals and run each of these:

bash
python server1.py     # backend on port 5001
python server2.py     # backend on port 5002
python server3.py     # backend on port 5003
python load_balancer.py   # load balancer on port 8080

Then hit http://127.0.0.1:8080 in your browser or with curl — refresh a few times and watch it rotate between servers.

To see the failover in action: stop any one of the backend servers while everything is running, and keep hitting the load balancer. It'll automatically stop routing to the dead server and only rotate between the ones still alive.

# Tech stack
- Python — socket, threading, queue (standard library only for the load balancer itself). Flask is used only for the disposable backend servers, since they don't need to teach anything — they're just there to be routed to.
