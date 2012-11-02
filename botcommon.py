"""\
Common bits and pieces used by the various bots.
"""

import sys
import os
import time
from threading import Thread, Event


class OutputManager(Thread):
  def __init__(self, connection, delay=.5):
    Thread.__init__(self)
    self.setDaemon(1)
    self.connection = connection
    self.delay = delay
    self.event = Event()
    self.queue = []

  def run(self):
    while 1:
      self.event.wait()
      while self.queue:
        msg,paste = self.queue.pop(0)
        self.connection.send(msg, paste)
        time.sleep(self.delay)
      self.event.clear()

  def send(self, msg, paste):
    self.queue.append((msg.strip(),paste))
    self.event.set()
