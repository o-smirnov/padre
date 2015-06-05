#!/usr/bin/python

import os.path
import os
import subprocess
import sys
import select
import time
import re
import socket

def find_unused_port (base,maxtries=1000):
    for i in range(maxtries):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            serversocket.bind(("localhost", base))
            serversocket.close()
            return base
        except:
            base += 1
            continue
    return None

default_port = os.environ.get("PADRE_REMOTE_PORT",5000+os.getuid()*10)
default_browser = os.environ.get("PADRE_BROWSER","xdg-open")

from optparse import OptionParser,OptionGroup
parser = OptionParser(usage="""%prog: [options] [user@]host[:radiopadre-path] directory [notebook.ipynb]""",
    description="Uses ssh to connect to remote host, runs radiopadre notebook server "+
    "in the specified directory, loads the specified notebook, if any."
)

# parser.add_option("--port-query",type=int,metavar="N",
#                   help="looks for N unused ports and reports them. For internal use.");
parser.add_option("-p","--port",type="int",default=default_port,
                  help="which base port to use. Default is %default, or set PADRE_REMOTE_PORT.")
parser.add_option("-b","--browser",type="string",default=default_browser,
                  help="browser command to run. Default is %default, or set PADRE_BROWSER.")
parser.add_option("-n","--no-browser",action="store_true",
                  help="do not open a browser.")

(options,args) = parser.parse_args()

# parse arguments
if len(args) == 2:
    host, directory = args
    notebook = None
elif len(args) == 3:
    host, directory, notebook = args
else:
    parser.error("incorrect number of arguments")

if ':' in host:
    host, padrepath = host.split(":",1)
    padrepath = os.path.join(padrepath,"run-radiopadre.sh")
else:
    padrepath = "run-radiopadre.sh"

print "Running remote radiopadre notebook on %s"%host

# start ssh subprocess to launch notebook
args = [ "ssh","-tt" ]
# for port in range(options.port,options.port+10):
#     args += [ "-L", "%d:localhost:%d" % (port, port) ]
args += [ host, "cd %s && %s" % (directory, padrepath) ]

ssh = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# poll stdout/stderr
poller = select.poll()
fdlabels = {}

def register_process (po,label=""):
    poller.register(po.stdout)
    poller.register(po.stderr)
    fdlabels[po.stdout.fileno()] = 'stdout'+label, po.stdout
    fdlabels[po.stderr.fileno()] = 'stderr'+label, po.stderr

register_process(ssh,"")

remoteport = ssh2 = None

while True:
    try:
        fdlist = poller.poll()
        for fd,event in fdlist:
            line = None
            if event & (select.POLLHUP|select.POLLERR):
                print "ssh process gone, exiting"
                sys.exit(0)
            # which fd is ready? read line and print it
            label,fobj = fdlabels.get(fd)
            line = fobj.readline()
            print "ssh %s: %s" % (label,line.strip())
            # if still looking for notebook port, check for it
            if not remoteport:
                match = line and re.match(".*Notebook is running at: http://localhost:([0-9]+)/.*",line)
                if match:
                    remoteport = match.group(1);
                    # find unused local port
                    localport = find_unused_port(10000+os.getuid())
                    print "Detected remote port %s, using local port %s" % (remoteport, localport)
                    # start second ssh process to forward the port
                    ssh2 = subprocess.Popen(["ssh","-tt","-L",
                                "%s:localhost:%s" % (localport, remoteport),
                                host,"cat >/dev/null"],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    register_process(ssh2)
                    # open browser if needed
                    path = "http://localhost:%s" % localport
                    if not options.no_browser:
                        print "Opening browser for",path
                        subprocess.Popen([options.browser, path])
                    else:
                        print "-n/--no-browser given, not opening a browser for you"
                        print "Please surf to",path
                    if notebook:
                        path = "http://localhost:%s/notebooks/%s" % (localport, notebook)
                        if not options.no_browser:
                            print "Opening browser for",path
                            subprocess.Popen([options.browser, path])
                        else:
                            print "Please surf to",path
    except KeyboardInterrupt:
        print "Ctrl+C caught"
        ssh.kill()
        ssh2 and ssh2.kill()