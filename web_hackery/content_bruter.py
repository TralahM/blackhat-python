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
import urllib.parse
import urllib.error

threads = 50
target_url = "http://testphp.vulnweb.com"
wordlist_file = os.path.join(os.path.abspath("."), "all.txt")  # from SVNDigger
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"


def build_wordlist(wordlist_file):
    # read i the wordlist
    with open(wordlist_file, "r") as fd:
        raw_words = fd.readlines()
    found_resume = False
    words = queue.Queue()
    for word in raw_words:
        word = word.rstrip()
        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print(f"[*] Resuming wordlist from : {resume}")
        else:
            words.put(word)
    return words


def dir_bruter(word_queue, extensions=None):
    while not word_queue.empty():
        attempt = word_queue.get()
        attempt_list = []
        # check if is a dir path or file
        if "." not in attempt:
            attempt_list.append(f"/{attempt}/")
        else:
            attempt_list.append(f"/{attempt}")
        # if we want to bruteforce extensions
        if extensions:
            [attempt_list.append(f"{attempt}{ext}") for ext in extensions]

        # iterate over our list of attempts
        for brute in attempt_list:
            url = f"{target_url}{urllib.parse.quote(brute)}"
            try:
                headers = {}
                headers["User-Agent"] = user_agent
                r = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(r)
                if len(response.read()):
                    print(f"{response.code} ==> {url}")
            except urllib.error.URLError as e:
                if hasattr(e, "code") and e.code != 404:
                    print(f"{e.code} ==> {url}")
                pass


if __name__ == "__main__":
    word_queue = build_wordlist(wordlist_file)
    extensions = [".php", ".bak", ".orig", ".inc"]
    for i in range(threads):
        print(f"Spawning thread: {i}")
        t = threading.Thread(
            target=dir_bruter,
            args=(
                word_queue,
                extensions,
            ),
        )
        t.start()
