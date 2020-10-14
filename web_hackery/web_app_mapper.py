#!/usr/bin/env python
"""Mapping Open Source Web App Installations.

Content Management Systems and blogging platforms such as Joomla,Wordpress, and
Drupal are relatively common in shared hosting environments or even enterprise
networks.

Because we can download any open source web application and locally determine its file and
directory structure, we can create a purpose-built scanner that can hunt for all files that are reachable
on the remote target. This can root out leftover installation files, directories that should be protected
by .htaccess files, and other goodies that can assist an attacker in getting a toehold on the web
server. This project also introduces you to using Python Queue objects, which allow us to build a
large, thread-safe stack of items and have multiple threads pick items for processing. This will allow
our scanner to run very rapidly.
"""
import queue
import threading
import os
import urllib
import urllib.request
import urllib.error

threads = 10

target = "http://www.blackhatpython.com"
directory = "~/Downloads/joomla-3.1.1"
filters = [".jpg", ".gif", ".png", ".css"]
CWD = os.path.abspath(".")
print(CWD)
os.chdir(os.path.expanduser(directory))
web_paths = queue.Queue()

for r, d, f in os.walk("."):
    for files in f:
        remote_path = "%s/%s" % (r, files)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(files)[1] not in filters:
            web_paths.put(remote_path)


def test_remote():
    pfd = open(f"{CWD}/urlpaths.txt", "w")
    resfd = open(f"{CWD}/web_map_results.txt", "w")
    while not web_paths.empty():
        path = web_paths.get()
        url = f"{target}{path}"
        pfd.write(url + "\n")
        request = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(request)
            content = response.read()
            print(f"{response.code} ==> {path} \t {content[:15]}")
            resfd.write(f"{response.code} ==> {path} \t {content[:15]}\n")
            response.close()
        except urllib.error.HTTPError as error:
            print(f"{error.code} : {error.reason}  ==> {path}")
            resfd.write(f"Failed {error.code} : {error.reason}  ==> {path}\n")
            pass
        except urllib.error.URLError as error:
            print(f"URLError : {error.reason} ==> {url}")
            pass
    pfd.close()
    resfd.close()


if __name__ == "__main__":
    for i in range(threads):
        print(f"Spawning thread: {i}")
        t = threading.Thread(target=test_remote)
        t.start()
