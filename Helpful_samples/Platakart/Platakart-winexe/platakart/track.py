# -*- coding: utf-8; -*-

import logging
from collections import namedtuple
from operator import itemgetter

logger = logging.getLogger("platakart.track")

from pubsub import pub
import pygame.display
import pygame.sprite
import pygame.draw
import pymunk
import pymunktmx.pygame_util
import pyscroll

from pymunktmx.shapeloader import load_shapes

from platakart.kart import CHECKPOINT_COLLISION_TYPE
from platakart.kart import KARTFACTORIES
from platakart.kart import Kart
from platakart.ui import Scene
from platakart.ui import ViewPort
from platakart.ui import ViewPortGroup


COLLISION_LAYERS = [2**i for i in range(32)]

# This crappy enumeration exists to make it easier to OR together the
# bitmasks for the different layers. I.E. layers = L1 | L2 | L3
L1, L2, L3, L4, L5, L6, L7, L8, L9, L10, \
    L11, L12, L13, L14, L15, L16, L17, L18, L19, \
    L20, L21, L22, L23, L24, L25, L26, L27, L28, \
    L29, L30, L31, L32 = COLLISION_LAYERS

# Up to 8 karts at the same time that don't hit eachother
KARTS_LAYERS = L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8

KartPerf = namedtuple(
    "KartPerf", "max_motor_rate, acceleration_rate, break_rate,"
    "wheel_friction")


class Semaphore(pygame.sprite.Sprite):
    """
    The Semaphore is implemented as a finite state machine. Below is a
    table of the states and their descriptions.

    State       Description
    -----------------------------------------------
    hidden    : retracted and not visible
    retracted : visible but retracted
    extending : animating to its extended position
    red       : extended and red light is on
    yellow    : extended yellow light is on
    green     : extended and green light is on
    retracting: animating to its retracted position

    Transitions:
    hidden     -> retracted
    retracted  -> extending | hidden
    extending  -> idle
    idle       -> red
    red        -> yellow
    yellow     -> green
    green      -> retracting
    retracting -> retracted
    """

    def __init__(self, retracted_position, extended_position,
                 red_surf, yellow_surf, green_surf, speed=5,
                 delay=2000):
        super(Semaphore, self).__init__()
        self.transitions = {"hidden": ("retracted",),
                            "retracted": ("extending", "hidden"),
                            "extending": ("idle",),
                            "idle": ("red",),
                            "red": ("yellow",),
                            "yellow": ("green",),
                            "green": ("retracting",),
                            "retracting": ("retracted",)}
        self.state = "hidden"
        self.visible = False
        self.retracted_position = retracted_position
        self.extended_position = extended_position
        self.speed = speed  # extension/retraction speed in pixels per second
        # the amount of time to wait in between light changes in milliseconds
        self.delay = delay
        self.time_waited = 0
        self.image = red_surf
        self.rect = red_surf.get_rect().move(retracted_position)
        self.topf = float(self.rect.top)
        self.red_surf = red_surf
        self.yellow_surf = yellow_surf
        self.green_surf = green_surf

    def transition(self, to_state):
        if to_state not in self.transitions[self.state]:
            msg = "The semaphore cannot transition from %s to %s"
            raise ValueError(msg % (self.state, to_state))

        old_state = self.state
        self.state = to_state
        self.on_transition(old_state, to_state)

    def on_transition(self, old_state, new_state):
        logger.debug("%s -> %s" % (old_state, new_state))
        cur_surf = self.image

        if new_state == "red":
            self.image = self.red_surf
        elif new_state == "yellow":
            self.image = self.yellow_surf
        elif new_state == "green":
            self.image = self.green_surf
        self.visible = new_state != "hidden"

        if cur_surf != self.image:
            self.rect = pygame.Rect(self.rect.topleft,
                                    self.image.get_rect().size)

        pub.sendMessage(
            "track.semaphore.state-change",
            old_state=old_state, new_state=new_state)
        logger.debug("Transitioned from %s to %s" % (old_state, new_state))

    def update(self, delta):
        if self.state == "hidden":
            return

        # TODO: There is some code duplication here to avoid function
        # calls or needless calculations. A refactoring should be
        # attempted if performance permits.
        if self.state == "extending":
            if self.rect.top < self.extended_position[1]:
                # convert delta from milliseconds to fractional seconds
                delta_secs = (float(delta) / 1000.0)
                self.topf += delta_secs * float(self.speed)
            elif self.rect.top >= self.extended_position[1]:
                self.topf = self.extended_position[1]
                self.time_waited = 0
                self.transition("idle")
        elif self.state == "retracting":
            if self.rect.top > self.retracted_position[1]:
                # convert delta from milliseconds to fractional seconds
                delta_secs = (float(delta) / 1000.0)
                self.topf -= delta_secs * self.speed
            elif self.rect.top <= self.retracted_position[1]:
                self.topf = self.retracted_position[1]
                self.transition("retracted")
        elif self.state == "red" or self.state == "yellow":
            self.time_waited += delta

            if self.time_waited >= self.delay:
                self.time_waited = 0
                if self.state == "red":
                    self.transition("yellow")
                elif self.state == "yellow":
                    self.transition("green")
        self.rect.top = int(self.topf)

    def show(self):
        self.transition("retracted")

    def hide(self):
        self.transition("hidden")

    def extend(self):
        self.transition("extending")

    def retract(self):
        self.transition("retracting")


class RaceManager(object):
    """Track and manage the various events that are emitted as a race
    progresses."""

    def __init__(self, track, semaphore, number_of_laps, checkpoints):
        self.checkpoints = checkpoints
        self.laps = dict()  # {kart_id: [lap time in ms, ...]}
        self.number_of_laps = number_of_laps  # number of laps to complete race
        self.race_clock = 0  # elapsed race time in ms
        self.race_complete = False
        self.race_started = False
        self.retracting_semaphore = False
        self.semaphore = semaphore
        self.semaphore = semaphore
        self.track = track
        self.track_scene = None

    def subscribe_events(self):
        pub.subscribe(
            self.on_semaphore_state_change, "track.semaphore.state-change")
        pub.subscribe(
            self.on_kart_entered_checkpoint, "kart.entered-checkpoint")

    def unsubscribe_events(self):
        pub.unsubscribe(
            self.on_semaphore_state_change, "track.semaphore.state-change")
        pub.unsubscribe(
            self.on_kart_entered_checkpoint, "kart.entered-checkpoint")

    def update(self, delta):
        semaphore = self.semaphore
        if not self.race_started:
            if semaphore.state == "retracted":
                self.track.set_friction(0.0)
                semaphore.extend()
            elif semaphore.state == "green":
                self.race_started = True
                semaphore.retract()
                self.track.set_friction()
            elif semaphore.state == "idle":
                semaphore.transition("red")
            elif semaphore.state == "hidden":
                semaphore.transition("retracted")
        elif self.race_started and semaphore.state == "extended":
            semaphore.retract()
        elif self.race_started and semaphore.state == "retracted":
            semaphore.hide()
            semaphore.kill()

        if not self.race_complete and self.race_started:
            self.race_clock += delta

    def on_kart_entered_checkpoint(self, kart, checkpoint_shape):
        if kart.checkpoint is None:
            # the track likely doesn't have checkpoints so bail
            return
        
        entered_checkpoint = next((cp for cp in self.checkpoints
                                   if cp[1] is checkpoint_shape))

        if entered_checkpoint is not kart.checkpoint:
            next_checkpoint = None
            lapped = False
            if kart.checkpoint is self.checkpoints[-1]:
                next_checkpoint = self.checkpoints[0]
                lapped = True
            else:
                next_checkpoint = self.checkpoints[kart.checkpoint[0] + 1]

            if entered_checkpoint is next_checkpoint:
                kart.checkpoint = next_checkpoint
                args = kart.perf.name, kart.id, next_checkpoint[0]
                logger.debug("%s{%s} advanced to checkpoint %d" % args)
                if lapped:
                    laps = self.laps.get(kart.id, list())
                    if len(laps) == 0:
                        laps.append(self.race_clock)
                    else:
                        laps.append(self.race_clock - sum(laps))
                    self.laps[kart.id] = laps
                    logger.debug(str(laps))
                    logger.debug("%s{%s} has advanced a lap!" %
                                 (kart.perf.name, kart.id))
                    logger.debug("Lap time was %d" % laps[-1])
        return True

    def on_semaphore_state_change(self, old_state, new_state):
        if new_state in ("red", "yellow"):
            pub.sendMessage("game.stop-sound", name="buzz")
            pub.sendMessage("game.play-sound", name="buzz")
        elif new_state == "green":
            pub.sendMessage("game.play-sound", name="buzzzz")


class PlayerDriver(object):
    """Player-controlled Kart driver"""

    def __init__(self, player_number):
        self.player_number = player_number
        self.kart = None
        prefix = "player%d" % player_number
        pub.subscribe(self.on_right, prefix + "-right")
        pub.subscribe(self.on_left, prefix + "-left")
        pub.subscribe(self.on_up, prefix + "-up")
        pub.subscribe(self.on_down, prefix + "-down")
        self.inputs = dict()
        # todo: sensitivity, or calibration of the stick

    def on_right(self, tilt_percent):
        self.inputs["right"] = tilt_percent

    def on_left(self, tilt_percent):
        self.inputs["left"] = tilt_percent

    def on_up(self, tilt_percent):
        self.inputs["up"] = tilt_percent

    def on_down(self, tilt_percent):
        self.inputs["down"] = tilt_percent

    def update(self):
        right = self.inputs.get("right", False)
        left = self.inputs.get("left", False)

        if right:
            self.kart.accelerate(Kart.RIGHT * right)
        elif left:
            self.kart.accelerate(Kart.LEFT * left)
        elif not left and not right and not self.inputs.get("down", False):
            self.kart.coast()

        if self.inputs.get("up", False):
            self.inputs["up"] = 0  # prevent kart from flying
            self.kart.jump()

        if self.inputs.get("down", False):
            self.kart.brake()


class RandomDriver(object):

    def __init__(self):
        self.kart = None

    def update(self):
        pass


class TrackScene(Scene):

    SEMAPHORE_END_POSITION = (0.6, 0.0)
    SEMAPHORE_SPEED = 800  # pixels per second

    def __init__(self, resources, conf):
        self.resources = resources
        self.karts = None
        self.map_data = None
        self.space = None
        self.step_amt = (1.0 / (float(conf.get("target_fps", 30)))) * (1/10.0)
        self.wireframe_mode = int(conf.get("wireframe_mode", 0))
        self.race_manager = None
        self.rect = None
        self.vpgroup = None
        self.hudgroup = None
        logger.debug("Calculated space step amount = %f" % self.step_amt)

    def get_name(self):
        return "track"

    def get_start_coordinates(self):
        start_position_obj = (o for o in self.map_data.tmx.getObjects()
                              if o.type == u"platakart_start_position").next()
        coords = (start_position_obj.x, start_position_obj.y)
        # we may not have a surface yet, so let's fake one.
        FakeSurf = namedtuple("FakeSurf", "get_height")
        height = self.tmx_data.height * self.tmx_data.tileheight
        surf = FakeSurf(lambda: height)
        return pymunktmx.pygame_util.from_pygame(coords, surf)

    def set_friction(self, x=None):
        """Sets the wheel friction for all karts to x. This is used at the
        beginning of the race to allow the karts to rev up their motors
        without moving anywhere."""
        for kart in self.karts:
            f = x
            if f is None:
                f = kart.perf.wheel_friction
            for wheel in kart.wheels:
                wheel.friction = f

    def get_semaphore(self):
        width_offset = self.SEMAPHORE_END_POSITION[0]
        height, width = self.resources.images["semaphore-red"].get_rect().size
        start_pos = (800 * width_offset, -height)
        end_pos = (start_pos[1], height)
        return Semaphore(
            start_pos, end_pos,
            self.resources.images["semaphore-red"],
            self.resources.images["semaphore-yellow"],
            self.resources.images["semaphore-green"],
            speed=self.SEMAPHORE_SPEED)

    def setup(self, options):
        logger.debug("Setting up track scene")
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        self.karts = list()

        track_name = options.get("trackname")
        self.tmx_data = self.resources.tilemaps[track_name]
        self.map_data = pyscroll.TiledMapData(self.tmx_data)
        shapes = load_shapes(self.tmx_data, space=self.space,
                             default_layers=KARTS_LAYERS)

        checkpoints = list()
        for name, shape in shapes.items():
            if name.startswith("checkpoint"):
                _, ordinal = name.split("_")
                ordinal = int(ordinal)
                checkpoints.append((ordinal, shape))
                shape.collision_type = CHECKPOINT_COLLISION_TYPE
        checkpoints.sort(key=itemgetter(0))

        self.vpgroup = ViewPortGroup(self.space, self.map_data, self.resources)
        self.hudgroup = pygame.sprite.Group()
        start_coords = self.get_start_coordinates()
        player_karts = options["player-karts"]

        for i, kart_id in enumerate(options["karts"]):
            record = self.resources.karts[kart_id]

            kart = KARTFACTORIES[record.model_id](
                record, self.resources, self.space,
                layers=COLLISION_LAYERS[i])

            if len(checkpoints) > 0:
                kart.checkpoint = checkpoints[0]

            kart.position = (start_coords[0] - (i * 25), start_coords[1])

            if kart_id in player_karts:
                kart.driver = PlayerDriver(player_karts[kart_id])

                # create new view for the kart
                vp = ViewPort()
                vp.follow(kart)
                self.vpgroup.add(vp)

            else:
                kart.driver = RandomDriver()

            for sprite in kart.sprites:
                if hasattr(sprite, "image"):
                    self.vpgroup.add(sprite)

            self.karts.append(kart)

        # fail if there are no players!
        if len(self.vpgroup) == 0:
            raise Exception

        semaphore = self.get_semaphore()
        self.hudgroup.add(semaphore)
        self.race_manager = RaceManager(self, semaphore, 6, checkpoints)
        self.race_manager.subscribe_events()

    def teardown(self):
        logger.debug("Tearing down track scene")
        self.race_manager.unsubscribe_events()

    def update(self, delta):
        """
        profiling notes:
        12 steps at 10 divisor is 'smooth and not fast' on core 2 duo -lt
        """
        # this looks awkward, but python loops are slow, and this loop
        # must be quick, so there is no loop here
        step_amt = self.step_amt
        step = self.space.step
        step(step_amt)  # 1
        step(step_amt)  # 2
        step(step_amt)  # 3
        step(step_amt)  # 4
        step(step_amt)  # 5
        step(step_amt)  # 6
        step(step_amt)  # 7
        step(step_amt)  # 8
        step(step_amt)  # 9
        step(step_amt)  # 10
        step(step_amt)  # 11
        step(step_amt)  # 12
        self.race_manager.update(delta)
        self.vpgroup.update(delta)
        self.hudgroup.update(delta)
        for kart in self.karts:
            kart.update(delta)

    def draw(self, surface, rect):
        if rect is not self.rect:
            self.rect = rect
        dirty = self.vpgroup.draw(surface, self.rect)
        # TODO: change hudgroup to a RenderedUpdates instance and
        # handle the dirty regions
        self.hudgroup.draw(surface)
        return dirty
