# -*- coding: utf-8; -*-

"""
Contains utilities for loading and writing Platakart configuration
INI files.
"""

from operator import itemgetter
from xml.etree import ElementTree
from collections import defaultdict
import ConfigParser
import codecs
import logging
import sys

from pygame import JOYAXISMOTION
from pygame import JOYBALLMOTION
from pygame import JOYBUTTONDOWN
from pygame import JOYBUTTONUP
from pygame import JOYHATMOTION
from pygame import KEYDOWN
from pygame import KEYUP
import pygame
import pygame.event

logger = logging.getLogger("platakart.config")

# Only include reasonable, sane defaults here. Copy and paste to
# add more players. Currently only 2 players supported.
DEFAULTS = {
    u"display_height": 480,
    u"display_width": 640,
    u"full_screen": 0,
    u"show_mini_map": 0,
    u"sound_enabled": 1,
    u"target_fps": 60,
    u"wireframe_mode": 0
}


def parse_config(config_path):
    parser = ConfigParser.SafeConfigParser()
    config = dict(DEFAULTS)

    try:
        parser.read(config_path)
        for section in parser.sections():
            config.update(parser.items(section))
    except Exception as ex:
        logger.error("Error parsing config file: %s" % str(config_path))
        logger.exception(ex)

    logger.debug("Config is: \n %s" % str(config))
    return config


def save_config(config_path, conf):
    if conf is None:
        conf = DEFAULTS

    parser = ConfigParser.ConfigParser()
    parser.add_section("platakart")
    for key, value in sorted(conf.items(), key=itemgetter(0)):
        if "-input-" in key:
            parser.set("platakart", key, value)

    with codecs.open(config_path, "wb", encoding="utf-8") as fob:
        parser.write(fob)

    logger.debug("Configuration written to %s" % str(config_path))


def nested_defaultdict():
    return defaultdict(nested_defaultdict)


class InputMap(object):

    def __init__(self):
        # key_enum: set([event_name, ...])
        self.keyboard_events = dict()

        # lookups are done as follows: events = buttons[1][1]
        # {joystick_number: {button_number: set([event_name, ...])}}
        self.button_events = dict()

        # lookups are done as follows: events = hat_events[1][1]["positive_y"]
        # {joystick_number:
        #     {axis/ball/hat number:
        #         {direction: set([event_name, ...])}}}
        self.hat_events = dict()
        self.axis_events = dict()
        self.ball_events = dict()
        self.events = list()
        self.joystick_deadzone = .20
        self.joystick_prev_state = defaultdict(dict)
        self.hat_prev_state = dict()

    def __repr__(self):
        s = u"InputMap: \n"

        s += u"Keyboard Events:\n"
        for key, value in self.keyboard_events.items():
            s += u"    %s = %s\n" % (key, unicode(value))
        s += "\n"

        s += u"Button Events:\n"
        for key, value in self.button_events.items():
            s += u"    %s = %s\n" % (key, unicode(value))
        s += "\n"

        s += u"Axis Events:\n"
        for key, value in self.axis_events.items():
            s += u"    %s = %s\n" % (key, unicode(value))
        s += "\n"

        s += u"Hat Events:\n"
        for key, value in self.hat_events.items():
            s += u"    %s = %s\n" % (key, unicode(value))
        s += "\n"

        s += u"Ball Events:\n"
        for key, value in self.ball_events.items():
            s += u"    %s = %s\n" % (key, unicode(value))
        s += "\n"

        return s

    def _complex_lookup(self, d, joystick_number, number, direction):
        events = set()
        joystick = d.get(joystick_number)
        if joystick is not None:
            num = joystick.get(number)
            if num is not None:
                event_names = num.get(direction)
                if event_names is not None:
                    events = event_names
        return events

    def yield_events(self):
        while len(self.events) != 0:
            yield self.events.pop()

    def handle_key_event(self, pg_event):
        event_names = self.keyboard_events.get(pg_event.key, list())
        tilt = 1.0 if pg_event.type == KEYDOWN else 0.0
        return [(name, tilt) for name in event_names]

    def handle_joybutton_event(self, pg_event):
        joystick = self.button_events.get(pg_event.joy)
        if joystick is not None:
            button = joystick.get(pg_event.button, list())
            tilt = 1.0 if pg_event.type == JOYBUTTONDOWN else 0.0
            return [(name, tilt) for name in button]
        return list()

    def handle_joyaxismotion_event(self, pg_event):
        # get the previous position of the axis
        joystick = self.joystick_prev_state[pg_event.joy]
        prev_direction = joystick.get(pg_event.axis, "center")

        # get the current position of the axis
        if pg_event.value < -self.joystick_deadzone:
            direction = "negative"
            pg_event.value = abs(pg_event.value)
        elif pg_event.value > self.joystick_deadzone:
            direction = "positive"
            pg_event.value = abs(pg_event.value)
        else:
            # axis is at the center position
            direction = prev_direction
            pg_event.value = 0

        # remember the current direction of the joystick
        joystick[pg_event.axis] = direction

        new_events = list()

        # generate a fake centering event, if not caught before
        if not direction == prev_direction and not prev_direction == "center":
            event_names = self._complex_lookup(
                self.axis_events, pg_event.joy, pg_event.axis, prev_direction)
            new_events.extend((name, 0) for name in event_names)

        # lookup events for the current position of the axis
        event_names = self._complex_lookup(
            self.axis_events, pg_event.joy, pg_event.axis, direction)

        # collect all the events for the current direction
        new_events.extend((name, pg_event.value) for name in event_names)

        return new_events

    def handle_joyballmotion_event(self, pg_event):
        cx, cy = pg_event.rel
        events = list()
        if cx != 0:
            if cx < 0:
                direction = "negative_x"
            elif cx > 0:
                direction = "positive_x"

            event_names = self._complex_lookup(
                self.ball_events, pg_event.joy,
                pg_event.ball, direction)
            for name in event_names:
                events.append((name, 1.0))

        if cy != 0:
            if cy < 0:
                direction = "negative_y"
            elif cy > 0:
                direction = "positive_y"

            event_names = self._complex_lookup(
                self.ball_events, pg_event.joy,
                pg_event.ball, direction)
            for name in event_names:
                events.append((name, 1.0))

        # simulate a depress event
        if cx == 0 and cy == 0:
            event_names = list()
            for direction in ("positive_x", "positive_y",
                              "negative_x", "negative_y"):
                self._complex_lookup(
                    self.ball_events, pg_event.joy,
                    pg_event.ball, direction)
                for name in event_names:
                    events.append((name, 0.0))

        # for the balls we need to add a JOYBALLMOTION event to the
        # pygame queue with no change so that it can emulate the
        # concept of depressed/not depressed
        fake_event = pygame.event.Event(
            JOYBALLMOTION, ball=pg_event.ball, rel=(0.0, 0.0))
        pygame.event.post(fake_event)
        return events

    def handle_joyhatmotion_event(self, pg_event):
        events = list()
        x, y = pg_event.value
        direction = None
        value = None

        if x < 0:
            direction = "negative_x"
            value = x
        elif x > 0:
            direction = "positive_x"
            value = x
        else:
            value = 0

        if y < 0:
            direction = "negative_y"
            value = y
        elif y > 0:
            direction = "positive_y"
            value = y
        else:
            value = 0

        # value is zero, so we have to find which axis changed
        if value == 0:
            joystick = self.joystick_prev_state.get(pg_event.joy, None)
            if joystick is None:
                joystick = dict()
                self.hat_prev_state[pg_event.joy] = joystick

            hat = joystick.get(pg_event.hat, None)
            if hat is None:
                direction = "center"
                joystick[pg_event.axis] = direction

        # lookup events for the current position of the hat
        event_names = self._complex_lookup(
            self.hat_events, pg_event.joy,
            pg_event.hat, direction)

        # remember the current direction of the hat
        # when an axis returns to center, we can use this value
        # to send a zero tilt to the correct axis
        if event_names:
            joystick = self.joystick_prev_state.get(pg_event.joy, None)
            if joystick is None:
                joystick = dict()
                self.hat_prev_state[pg_event.joy] = joystick
            joystick[pg_event.hat] = pg_event.value

        return [(name, value) for name in event_names]

    def update(self, pygame_events):
        for pg_event in pygame_events:
            t = pg_event.type

            # an event is a tuple (name, tilt_percent). tilt_percent is
            # automatically 100%/0% for buttons, keyboard keys and balls
            events = list()
            if t == KEYDOWN or t == KEYUP:
                events = self.handle_key_event(pg_event)
            elif t == JOYBUTTONDOWN or t == JOYBUTTONUP:
                events = self.handle_joybutton_event(pg_event)
            elif t == JOYAXISMOTION:
                events = self.handle_joyaxismotion_event(pg_event)
            elif t == JOYBALLMOTION:
                events = self.handle_joyballmotion_event(pg_event)
            elif t == JOYHATMOTION:
                events = self.handle_joyhatmotion_event(pg_event)

            for event in events:
                self.events.insert(0, event)

    def add_keyboard_mapping(self, event_name, key_enum):
        events = self.keyboard_events.get(key_enum, None)
        if events is None:
            events = set()
            self.keyboard_events[key_enum] = events
        events.add(event_name)

    def add_button_mapping(self, event_name, joystick_number, button_number):
        joystick = self.button_events.get(joystick_number, None)
        if joystick is None:
            joystick = dict()
            self.button_events[joystick_number] = joystick

        button = joystick.get(button_number, None)
        if button is None:
            button = set()
            joystick[button_number] = button

        button.add(event_name)

    def _add_complex_mapping(self, target_dict, event_name, joystick_number,
                             axis_number, direction):
        joystick = target_dict.get(joystick_number, None)
        if joystick is None:
            joystick = dict()
            target_dict[joystick_number] = joystick

        axis = joystick.get(axis_number, None)
        if axis is None:
            axis = dict()
            joystick[axis_number] = axis

        events = axis.get(direction, None)
        if events is None:
            events = set()
            axis[direction] = events

        events.add(event_name)

    def add_axis_mapping(self, event_name, joystick_number,
                         axis_number, direction):
        self._add_complex_mapping(
            self.axis_events, event_name, joystick_number,
            axis_number, direction)

    def add_hat_mapping(self, event_name, joystick_number,
                        hat_number, direction):
        self._add_complex_mapping(
            self.hat_events, event_name, joystick_number,
            hat_number, direction)


def parse_keyboard_control_config(node, event_name, input_map):
    for keyboard_node in node.findall("keyboard"):
        for key_node in keyboard_node.findall("key"):
            enum = key_node.get("enum", "")
            if len(enum) == 0:
                logger.error("Invalid or missing enum for key binding")
            else:
                input_map.add_keyboard_mapping(
                    event_name, getattr(pygame, enum))


def parse_joystick_control_config(node, event_name, input_map):
    # get the joystick number
    joystick_number = node.get("number", "")
    if len(joystick_number) == 0:
        logger.error("Invalid joystick number %s"
                     % str(joystick_number))

    try:
        joystick_number = int(joystick_number)
    except (ValueError, TypeError) as ex:
        logger.error("Invalid joystick number %s"
                     % str(joystick_number))
        logger.exception(ex)
        return

    # filter down the nodes to just the 4 types we care about
    input_types = set(["axis", "ball", "button", "hat"])
    nodes = (n for n in node if n.tag.lower() in input_types)
    for node in nodes:
        # all of these nodes have number attributes, so get it
        number = node.get("number", "")
        if len(number) == 0:
            logger.error(
                "%s node missing number attribute" % node.tag)
        try:
            number = int(number)
        except (ValueError, TypeError) as ex:
            logger.exception(ex)
            logger.error(
                "%s node has invalid number attribute" % node.tag)
            continue

        if node.tag.lower() == "button":
            input_map.add_button_mapping(
                event_name, joystick_number, number)
        else:
            # the rest of the nodes will have a direction attribute
            directions = set(["positive_y", "negative_y",
                              "positive_x", "negative_x"])
            axis_directions = set(["positive", "negative"])
            all_directions = directions | axis_directions
            direction = node.get("direction", "").lower()
            if direction not in all_directions:
                logger.error("%s node has an invalid direction attribute '%s'"
                             % (node.tag, direction))
            else:
                tag = node.tag.lower()
                if tag == "axis":
                    if direction not in axis_directions:
                        logger.error("Axis node has an invalid direction "
                                     "attribute '%s'" % direction)
                    else:
                        input_map.add_axis_mapping(
                            event_name, joystick_number, number,
                            direction)
                else:
                    if direction not in axis_directions:
                        logger.error("%s node has an invalid direction "
                                     "attribute '%s'" % (tag, direction))
                    else:
                        if tag == "ball":
                            input_map.add_ball_mapping(
                                event_name, joystick_number,
                                number, direction)
                        if tag == "hat":
                            input_map.add_hat_mapping(
                                event_name, joystick_number,
                                number, direction)


def parse_control_config(config_path):
    etree = ElementTree.parse(config_path).getroot()
    input_map = InputMap()
    for node in etree.findall("input"):
        event_name = node.get("eventname", "")
        if len(event_name) == 0:
            raise ValueError("Invalid or missing eventname for input")

        parse_keyboard_control_config(node, event_name, input_map)

        # joystick parsing
        for joystick_node in node.findall("joystick"):
            parse_joystick_control_config(joystick_node, event_name, input_map)

    logger.debug(str(input_map))
    return input_map
