#!/usr/bin/env python

import sys, time
from daemon import Daemon
import multiprocessing
import socket
from api import queue
from deploy import deploy_container
import subprocess

class MyDaemon(Daemon):
    def run(self):
        print('Generating queue...')
        q = queue.gen_queue('localhost', 6379, '')
        print('Done')
        threads = dict()
        containers = dict()
        print('Getting number of threads %s can handle...' % socket.gethostname())

        threads[socket.gethostname()] = multiprocessing.cpu_count()
        containers[socket.gethostname()] = 0
        print('Threads: %s' % threads[socket.gethostname()])
        while True:
            jobs = len(q)
            if ((containers[socket.gethostname()] < jobs) and
                (containers[socket.gethostname()] <= threads[socket.gethostname()])):
                print('Containers(%s) < jobs(%s).  Spinning up new container' %
                    (containers[socket.gethostname()], jobs))
                res = deploy_container(socket.gethostname())
                if res == 1:
                    print('Error on container spin up.')
                    continue
                containers[socket.gethostname()] += 1
            time.sleep(1)


if __name__ == "__main__":

    daemon = MyDaemon('/tmp/daemon-example.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print('Starting master control daemon...')
            daemon.start()
        elif 'stop' == sys.argv[1]:
			daemon.stop()
        elif 'restart' == sys.argv[1]:
			daemon.restart()
        else:
			print("Unknown command")
			sys.exit(2)
        sys.exit(0)
    else:
		print("usage: %s start|stop|restart" % sys.argv[0])
		sys.exit(2)
