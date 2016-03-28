"""
PC-BASIC - signals.py
Queues and signals for communication between interpreter and interface

(c) 2013, 2014, 2015, 2016 Rob Hagemans
This file is released under the GNU GPL version 3 or later.
"""

import Queue


###############################################################################
# initialisation

def prepare():
    """ Initialise signals module. """


###############################################################################
# queues

video_queue = Queue.Queue()
input_queue = Queue.Queue()
# audio queues
message_queue = Queue.Queue()
tone_queue = [Queue.Queue(), Queue.Queue(), Queue.Queue(), Queue.Queue()]


def save_queue(q):
    """ Get list of queue tasks. """
    qlist = []
    while True:
        try:
            qlist.append(q.get(False))
            q.task_done()
        except Queue.Empty:
            break
    return qlist

def load_queue(q, qlist):
    """ Initialise queue from list of tasks. """
    for item in qlist:
        q.put(item)


###############################################################################
# signals

class Event(object):
    """ Signal object for input, video or audio queue. """

    def __init__(self, event_type, params=None):
        """ Create signal. """
        self.event_type = event_type
        self.params = params


# audio queue signals
AUDIO_TONE = 0
AUDIO_STOP = 1
AUDIO_NOISE = 2
AUDIO_QUIT = 4
AUDIO_PERSIST = 6

# video queue signals
# save state and quit
VIDEO_QUIT = 0
# change video mode
VIDEO_SET_MODE = 1
# switch page
VIDEO_SET_PAGE = 2
# set cursor shape
VIDEO_SET_CURSOR_SHAPE = 3
# move cursor
VIDEO_MOVE_CURSOR = 5
# set cursor attribute
VIDEO_SET_CURSOR_ATTR = 6
# set border attribute
VIDEO_SET_BORDER_ATTR = 7
# put character glyph
VIDEO_PUT_GLYPH = 8
# clear rows
VIDEO_CLEAR_ROWS = 10
# scroll
VIDEO_SCROLL_UP = 11
VIDEO_SCROLL_DOWN = 12
# set colorburst
VIDEO_SET_COLORBURST = 13
# show/hide cursor
VIDEO_SHOW_CURSOR = 14
# set palette
VIDEO_SET_PALETTE = 15
# build glyphs
VIDEO_BUILD_GLYPHS = 16
# put pixel
VIDEO_PUT_PIXEL = 17
# put interval
VIDEO_PUT_INTERVAL = 18
VIDEO_FILL_INTERVAL = 19
# put rect
VIDEO_PUT_RECT = 20
VIDEO_FILL_RECT = 21
# copy page
VIDEO_COPY_PAGE = 28
# set caption message
VIDEO_SET_CAPTION = 29
# clipboard copy reply
VIDEO_SET_CLIPBOARD_TEXT = 30

# input queue signals
# special keys
KEYB_QUIT = 0
# insert character
KEYB_CHAR = 4
# insert keydown
KEYB_DOWN = 5
# insert keyup
KEYB_UP = 6
# light pen events
PEN_DOWN = 101
PEN_UP = 102
PEN_MOVED = 103
# joystick events
STICK_DOWN = 201
STICK_UP = 202
STICK_MOVED = 203
# clipboard events
CLIP_COPY = 254
CLIP_PASTE = 255


###############################################################################

prepare()