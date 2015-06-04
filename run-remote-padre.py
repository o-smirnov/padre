#!/usr/bin/python

import os.path
import os
import subprocess
import sys
import select
import time
import re

default_port = os.environ.get("PADRE_REMOTE_PORT",5000+os.getuid()*10)
default_browser = os.environ.get("PADRE_BROWSER","xdg-open")

from optparse import OptionParser,OptionGroup
parser = OptionParser(usage="""%prog: [options] [user@]host[:run-radiopadre-path] directory [notebook.ipynb]""",
    description="Uses ssh to connect to remote host, runs radiopadre notebook server "+
    "in the specified directory, loads the specified notebook, if any."
)

parser.add_option("-p","--port",type="int",default=default_port,
                  help="which base port to use. Default is %default, or set PADRE_REMOTE_PORT.")
parser.add_option("-b","--browser",type="string",default=default_browser,
                  help="browser command to run. Default is %default, or set PADRE_BROWSER.")
parser.add_option("-n","--no-browser",action="store_true",
                  help="do not open a browser.")

(options,args) = parser.parse_args()

if len(args) == 2:
    host, directory = args
    notebook = None
elif len(args) == 3:
    host, directory, notebook = args
else:
    parser.error("incorrect number of arguments")

if ':' in host:
    host, padrepath = host.split(":",1)
else:
    padrepath = "run-radiopadre.sh"

# start subprocess
args = [ "ssh","-tt" ]
for port in range(options.port,options.port+10):
    args += [ "-L", "%d:localhost:%d" % (port, port) ]
args += [ host, "cd %s && %s" % (directory, padrepath) ]

ssh = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

poller = select.poll()
poller.register(ssh.stdout)
poller.register(ssh.stderr)

while True:
    try:
        fdlist = poller.poll()
        for fd,event in fdlist:
            line = None
            if event & (select.POLLHUP|select.POLLERR):
                print "Exiting"
                sys.exit(0)
            if fd == ssh.stdout.fileno():
                line = ssh.stdout.readline()
                print "ssh stdout: ",line.strip()
            elif fd is ssh.stderr.fileno():
                line = ssh.stderr.readline()
                print "ssh stderr: ",line.strip()
            match = line and re.match(".*Notebook is running at: http://localhost:([0-9]+)/.*",line)
            if match:
                port = match.group(1);
                path = "http://localhost:"+port
                if not options.no_browser:
                    print "Opening browser for",path
                    subprocess.Popen([options.browser, path])
                else:
                    print "-n/--no-browser given, not opening a browser for you"
                    print "Please surf to",path
                if notebook:
                    path = "http://localhost:"+port+"/notebooks/"+notebook
                    if not options.no_browser:
                        print "Opening browser for",path
                        subprocess.Popen([options.browser, path])
                    else:
                        print "Please surf to",path
    except KeyboardInterrupt:
        print "Ctrl+C caught"
        ssh.kill()
