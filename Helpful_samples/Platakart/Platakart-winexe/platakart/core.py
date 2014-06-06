# -*- coding: utf-8; -*-

from collections import namedtuple
from pubsub import pub
import ConfigParser
import logging
import os.path

logger = logging.getLogger("platakart.core")

from pygame.time import Clock
import pygame
import pygame.event
import pygame.font
import pygame.joystick
import pytmx

from platakart.config import parse_config
from platakart.config import parse_control_config
from platakart.controllerconf import ControllerConfScene
from platakart.kartselect import KartSelectScene
from platakart.circuitselect import CircuitSelectScene
from platakart.title import TitleScene
from platakart.track import TrackScene
from platakart.trackselect import TrackSelectScene
from platakart.kart import KartRecord

SHOWFPSEVENT = pygame.USEREVENT + 1
GAMETITLE = "Platakart"

from collections import namedtuple
CircuitRecord = namedtuple(
    "CircuitRecord",
    [
        "id",
        "name",
        "descriptions",
        "difficulty",
        "tracks",
        "thumbnail",
    ])


class Resources(object):

    def __init__(self, path=None):
        self.images = dict()
        self.sounds = dict()
        self.tilemaps = dict()
        self.fonts = dict()
        self.karts = dict()
        self.circuits = dict()
        if path is None:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            self.path = os.path.join(current_dir, "resources")
        else:
            self.path = path
        self.config_path = os.path.join(self.path, "resources.ini")
        self.loaded = False

    def load_images(self):
        for key, path in self.images.items():
            full_path = os.path.join(self.path, path)
            img = pygame.image.load(full_path).convert_alpha()
            temp = pygame.Surface(img.get_size())
            temp.fill((255, 0, 255))
            temp.blit(img, (0, 0))
            temp.set_colorkey((255, 0, 255))
            self.images[key] = temp
            logger.debug("Loaded image %s" % full_path)
            yield "image", key

    def load_sounds(self):
        for key, path in self.sounds.items():
            full_path = os.path.join(self.path, path)
            self.sounds[key] = pygame.mixer.Sound(full_path)
            logger.debug("Loaded sound %s" % full_path)
            yield "sound", key

    def load_tilemaps(self):
        for key, path in self.tilemaps.items():
            full_path = os.path.join(self.path, path)
            self.tilemaps[key] = pytmx.load_pygame(full_path)
            logger.debug("Loaded tilemap %s" % full_path)
            yield "tilemap", key

    def load_fonts(self):
        yield None, None

    def load_config(self):
        parser = ConfigParser.SafeConfigParser()
        parser.read(self.config_path)
        self.images.update(parser.items("images"))
        self.sounds.update(parser.items("sounds"))
        self.tilemaps.update(parser.items("tilemaps"))
        self.fonts.update(parser.items("fonts"))

    def load_karts(self):
        parser = ConfigParser.SafeConfigParser()
        karts_path = os.path.join(self.path, "karts.ini")
        parser.read(karts_path)
        for section in parser.sections():
            get = lambda k: parser.get(section, k)
            get_float = lambda k: parser.getfloat(section, k)
            id = section
            acceleration_rate = get_float(u"acceleration_rate")
            body_surf = get(u"body_surf")
            brake_rate = get_float(u"brake_rate")
            coast_rate = get_float(u"coast_rate")
            chassis_mass = get_float(u"chassis_mass")
            damping = get_float(u"damping")
            stiffness = get_float(u"stiffness")
            description = get(u"description")
            front_wheel_offset_percent = get_float(
                u"front_wheel_offset_percent")
            rear_wheel_offset_percent = get_float("rear_wheel_offset_percent")
            jump_impulse = get_float(u"jump_impulse")
            max_motor_rate = get_float(u"max_motor_rate")
            if parser.has_option(section, "model_id"):
                model_id = get(u"model_id")
            else:
                model_id = "default"
            name = get("name")
            select_thumb = get("select_thumb")
            wheel_friction = get_float("wheel_friction")
            wheel_mass = get_float("wheel_mass")
            wheel_surf = get("wheel_surf")
            wheel_vertical_offset = get_float("wheel_vertical_offset")

            # the best way to make sure these args don't get out of
            # order, is to put 'id' first, then sort the rest of the
            # args in alphabetical order.
            self.karts[id] = KartRecord(
                id,
                acceleration_rate,
                body_surf,
                brake_rate,
                chassis_mass,
                coast_rate,
                damping,
                description,
                front_wheel_offset_percent,
                jump_impulse,
                max_motor_rate,
                model_id,
                name,
                rear_wheel_offset_percent,
                select_thumb,
                stiffness,
                wheel_friction,
                wheel_mass,
                wheel_surf,
                wheel_vertical_offset
            )

    def load_circuits(self):
        parser = ConfigParser.SafeConfigParser()
        circuits_path = os.path.join(self.path, "circuits.ini")
        parser.read(circuits_path)
        for section in parser.sections():
            get = lambda k: parser.get(section, k)
            get_int = lambda k: parser.getint(section, k)
            id = section
            name = get(u"name")
            description = get(u"description")
            difficulty = get_int(u"difficulty")
            tracks = get(u"tracks")
            tracks = tuple(i.strip() for i in tracks.split(u","))
            thumbnail = get(u"thumbnail")

            self.circuits[id] = CircuitRecord(
                id,
                name,
                description,
                difficulty,
                tracks,
                thumbnail
            )

    def load(self):
        if self.loaded:
            return
        self.load_config()
        self.load_karts()

        msg = "Kart %s specified %s (%s) was not configured in resources.ini"
        props = set(["body_surf", "wheel_surf", "select_thumb"])
        for kart in self.karts.values():
            for prop in props:
                if getattr(kart, prop) not in self.images:
                    raise KeyError(
                        msg % (kart.name, prop, getattr(kart, prop)))
        dicts = (self.images, self.sounds, self.tilemaps, self.fonts)
        total = sum(map(len, dicts))
        loaded = 0
        logger.debug(
            "Loading resources from config: %s" % str(self.config_path))
        gens = (self.load_images, self.load_sounds, self.load_tilemaps,
                self.load_fonts)

        for gen in gens:
            for category, key in gen():
                loaded += 1
                pub.sendMessage("resources.loading",
                                percent=float(loaded) / float(total),
                                category=category,
                                key=key)
                yield

        self.load_circuits()

        # check the circuits for consistency
        msg = "Circuit %s specified %s (%s) was not configured in resources.ini"
        props = set(["thumbnail"])
        all_tracks = set(self.tilemaps.keys())
        for circuit in self.circuits.values():
            for prop in props:
                if getattr(circuit, prop) not in self.images:
                    raise KeyError(
                        msg % (circuit.name, prop, getattr(circuit, prop)))
            for track in circuit.tracks:
                if track not in all_tracks:
                    raise KeyError(msg % (circuit.name, track))

        self.loaded = True
        pub.sendMessage("resources.loaded")


class Game(object):

    def __init__(self, config, scenes, starting_scene, resources, input_map):
        self.clock = Clock()
        self.config = config
        self.shutting_down = False
        self.scenes = scenes
        self.current_scene = starting_scene
        self.resources = resources
        self.joysticks = list()
        self.input_map = input_map

        try:
            self.display_width = int(config.get("display_width", 640))
        except ValueError:
            logger.warning("Invalid DISPLAY_WIDTH")
            self.display_width = 640

        try:
            self.display_height = int(config.get("display_height", 480))
        except ValueError:
            logger.warning("Invalid DISPLAY_HEIGHT")
            self.display_height = 480

        self.display_size = (self.display_width, self.display_height)
        pub.subscribe(self.switch_scene, "game.switch-scene")
        pub.subscribe(self.play_sound, "game.play-sound")
        pub.subscribe(self.stop_sound, "game.stop-sound")

    def init_pygame(self):
        logger.debug("Initializing pygame")
        pygame.display.init()
        pygame.font.init()
        pygame.mixer.init()

        flags = 0

        if self.config.get("full_screen", 0) == 1:
            flags = flags | pygame.FULLSCREEN

        screen = pygame.display.set_mode(self.display_size, flags)
        pygame.display.set_caption(GAMETITLE)

        logger.debug("Initializing joystick support")
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        logger.debug("Provisioning %d joysticks" % joystick_count)

        for i in range(joystick_count):
            js = pygame.joystick.Joystick(i)
            js.init()
            self.joysticks.append(js)

        return screen

    def switch_scene(self, name, options):
        self.current_scene.teardown()
        self.current_scene = self.scenes[name]
        if options is None:
            self.current_scene.setup()
        else:
            self.current_scene.setup(dict(options))

    def play_sound(self, name=None, loops=0, maxtime=0, fade_ms=0):
        if int(self.config.get("sound_enabled", 0)):
            self.resources.sounds[name].play(loops, maxtime, fade_ms)

    def stop_sound(self, name=None, fade_ms=0):
        if fade_ms == 0:
            self.resources.sounds[name].stop()
        else:
            self.resources.sounds[name].fadeout(fade_ms)

    def main_loop(self):
        screen = self.init_pygame()

        logger.debug("Entering main loop")
        try:
            self._main_loop(screen)
        except KeyboardInterrupt:
            logger.debug("Keyboard interrupt received")
        logger.debug("Shutting down main loop")
        pygame.quit()

    def _main_loop(self, screen):
        # Get references to things that will be used in every frame to
        # avoid needless derefrencing.
        target_fps = float(self.config.get("target_fps", 30))
        pump = pygame.event.pump
        get = pygame.event.get
        QUIT = pygame.QUIT
        MOUSEMOTION = pygame.MOUSEMOTION
        MOUSEBUTTONDOWN = pygame.MOUSEBUTTONDOWN
        MOUSEBUTTONUP = pygame.MOUSEBUTTONUP
        pygame.time.set_timer(SHOWFPSEVENT, 3000)
        self.current_scene.setup()
        rect = screen.get_rect()
        while not self.shutting_down:
            pump()
            events = get()

            # give the game class the first stab at the events
            for event in events:
                t = event.type
                if t == QUIT:
                    self.shutting_down = True
                    break
                elif t == SHOWFPSEVENT:
                    logger.debug("FPS: %d" % self.clock.get_fps())
                elif t == MOUSEMOTION:
                    pub.sendMessage("input.mouse-move", pos=event.pos,
                                    rel=event.rel, buttons=event.buttons)
                elif t == MOUSEBUTTONDOWN:
                    pub.sendMessage("input.mouse-down", pos=event.pos,
                                    button=event.button)
                elif t == MOUSEBUTTONUP:
                    pub.sendMessage("input.mouse-up", pos=event.pos,
                                    button=event.button)

            # delegate the rest of the events to the InputMap
            self.input_map.update(events)
            for event_name, tilt_percent in self.input_map.yield_events():
                logger.debug("Emitting %s event with %f tilt"
                             % (event_name, tilt_percent))
                pub.sendMessage(event_name, tilt_percent=tilt_percent)

            delta = self.clock.tick(target_fps)
            self.current_scene.update(delta)

            dirty = self.current_scene.draw(screen, rect)
            pygame.display.update(dirty)


def create_game(config_path, control_config_path, resource_path=None):
    conf = parse_config(config_path)
    input_map = parse_control_config(control_config_path)

    resources = Resources(resource_path)
    scenes = {"title": TitleScene(resources),
              "kart-select": KartSelectScene(resources),
              "track-select": TrackSelectScene(resources),
              "circuit-select": CircuitSelectScene(resources),
              "controller-conf": ControllerConfScene(),
              "track": TrackScene(resources, conf)}
    g = Game(conf, scenes, scenes["title"], resources, input_map)
    return g
