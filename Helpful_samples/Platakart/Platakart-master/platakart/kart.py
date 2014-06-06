from collections import namedtuple
from uuid import uuid4
import itertools
import logging

import pygame
import pymunk
from pubsub import pub

from platakart.sprite import CircleSprite, BoxSprite

logger = logging.getLogger(__name__)

CHECKPOINT_COLLISION_TYPE = 2

KartRecord = namedtuple(
    "KartRecord",
    [
        "id",
        "acceleration_rate",
        "body_surf",
        "brake_rate",
        "chassis_mass",
        "coast_rate",
        "damping",
        "description",
        "front_wheel_offset_percent",
        "jump_impulse",
        "max_motor_rate",
        "model_id",
        "name",
        "rear_wheel_offset_percent",
        "select_thumb",
        "stiffness",
        "wheel_friction",
        "wheel_mass",
        "wheel_surf",
        "wheel_vertical_offset"
    ])


# TODO: this should be a generic "sprite bundle" class, maybe
class Kart(object):
    RIGHT = 1
    LEFT = -1

    def __init__(self, perf, id_fn=uuid4):
        super(Kart, self).__init__()
        self.id = id_fn()
        self.perf = perf

        self._driver = None
        self.direction = self.LEFT
        self.chassis_direction = self.LEFT
        self.chassis = None
        self.wheels = list()
        self.motors = list()
        self.checkpoint = None  # the last checkpoint the kart entered

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, value):
        self._driver = value
        self._driver.kart = self

    @property
    def sprites(self):
        return list(itertools.chain(self.wheels, [self.chassis]))

    @property
    def position(self):
        return self.chassis.shape.body.position

    @position.setter
    def position(self, value):
        position = pymunk.Vec2d(value)
        self.chassis.shape.body.position += position
        for wheel in self.wheels:
            wheel.shape.body.position += position

    def update(self, delta):
        self.driver.update()

    def accelerate(self, direction):
        this_direction = None
        if direction > 0:
            this_direction = self.RIGHT
        if direction < 0:
            this_direction = self.LEFT

        if not this_direction == self.chassis_direction:
            self.chassis.flipped = this_direction == self.RIGHT
            self.chassis_direction = this_direction

        amt = direction * self.perf.acceleration_rate
        for motor in self.motors:
            motor.max_force = pymunk.inf
            if abs(motor.rate + amt) < self.perf.max_motor_rate:
                motor.rate += amt

    def coast(self):
        for motor in self.motors:
            motor.rate = 0
            motor.max_force = self.perf.coast_rate

    def brake(self):
        for motor in self.motors:
            motor.rate = 0
            motor.max_force = self.perf.brake_rate

    def jump(self):
        impulse = (0, self.perf.jump_impulse)
        self.chassis.shape.body.apply_impulse(impulse)
        for wheel in self.wheels:
            wheel.shape.body.apply_impulse(impulse)

    def on_enter_checkpoint(self, space, arbitor):
        pub.sendMessage(
            "kart.entered-checkpoint",
            kart=self, checkpoint_shape=arbitor.shapes[1])
        return True


# Factory functions for different kart models are registered in this
# dict in order to facilitate model creation in the track scene. A
# corresponding attribute in karts.ini called model_id is used to
# specify the model for a kart record. If model_id is not provided,
# the default model will be used.
#
# dict contents: {model_id: factory_function}
KARTFACTORIES = dict()


def kart_factory_fn(model_id):
    """This decorator is used to easily register a factory function in
    the KARTFACTORIES dict."""

    def wrapper(fn):
        logger.debug("Wrapper called")
        KARTFACTORIES[model_id] = fn
        return fn
    return wrapper


@kart_factory_fn("default")
def kart_factory(record, resources, space, layers=-1):
    """
    Notes:

    #1: should the shapes' size be defined by the image given, or data in tmx?
    """
    def make_chassis(surface):
        rect = surface.get_rect()
        half_width = rect.width / 2.0
        inertia = pymunk.moment_for_segment(
            record.chassis_mass, (-half_width, 0), (half_width, 0))
        body = pymunk.Body(record.chassis_mass, inertia)
        shape = pymunk.Segment(
            body, (-half_width, 0), (half_width, 0), rect.height // 2)
        return body, shape

    def make_wheel(surface):
        rect = surface.get_rect()
        radius = rect.width // 2
        inertia = pymunk.moment_for_circle(
            record.wheel_mass, 0, radius, (0, 0))
        body = pymunk.Body(record.wheel_mass, inertia)
        shape = pymunk.Circle(body, radius, (0, 0))
        shape.friction = record.wheel_friction
        return body, shape

    body_surf = resources.images[record.body_surf]
    wheel_surf = resources.images[record.wheel_surf]

    motors = list()
    wheel_sprites = list()

    # build chassis
    chassis_body, chassis_shape = make_chassis(body_surf)
    chassis_shape.layers = layers
    chassis_sprite = BoxSprite(chassis_shape, body_surf)
    space.add(chassis_body, chassis_shape)

    # build wheels
    for h_offset_percent in [record.front_wheel_offset_percent,
                             record.rear_wheel_offset_percent]:
        body, shape = make_wheel(wheel_surf)
        shape.layers = layers
        body_rect = chassis_sprite.rect

        wheel_offset = ((body_rect.width * h_offset_percent)
                        - body_rect.width / 2)

        body.position = (chassis_body.position.x + wheel_offset,
                         chassis_body.position.y - (shape.radius * 1.5))

        motor = pymunk.SimpleMotor(chassis_body, body, 0.0)

        spring = pymunk.DampedSpring(
            body,
            chassis_body,
            (0, 0),
            (wheel_offset, -body_rect.height * 2),
            50.0,
            record.stiffness,
            record.damping)

        vertical_offset = record.wheel_vertical_offset * body_rect.height
        joint = pymunk.GrooveJoint(
            chassis_body, body,
            (wheel_offset, -body_rect.height),
            (wheel_offset, -vertical_offset - (shape.radius * 1.5)),
            (0, 0))

        sprite = CircleSprite(shape, wheel_surf)
        wheel_sprites.append(sprite)
        motors.append(motor)
        space.add(body, shape, motor, spring, joint)

    kart = Kart(record)
    kart.chassis = chassis_sprite
    kart.wheels = wheel_sprites
    kart.motors = motors
    kart_object_id = id(kart)

    for wheel in kart.wheels:
        wheel.shape.collision_type = kart_object_id

    space.add_collision_handler(
        kart_object_id,
        CHECKPOINT_COLLISION_TYPE,
        kart.on_enter_checkpoint)
    return kart


@kart_factory_fn("boxkart")
def boxkart_factory(record, resources, space, layers=-1):

    def make_chassis(surface):
        rect = pygame.Rect(0, 0, 2, 2)
        w = rect.width
        body = pymunk.Body(record.chassis_mass, pymunk.inf)
        shape = pymunk.Poly.create_box(body, (w, w))
        return body, shape

    def make_wheel(surface):
        rect = surface.get_rect()
        w = rect.width
        inertia = pymunk.moment_for_box(record.wheel_mass, w, w)
        body = pymunk.Body(record.wheel_mass, inertia)
        shape = pymunk.Poly.create_box(body, (w, w))
        return body, shape

    surf = resources.images[record.wheel_surf]
    surf = pygame.transform.scale(surf, (128, 128))

    body_surf = pygame.Surface((32, 32), flags=pygame.SRCALPHA)
    wheel_surf = surf

    motors = list()
    wheel_sprites = list()

    # build chassis
    chassis_body, chassis_shape = make_chassis(body_surf)
    chassis_shape.layers = 0
    chassis_sprite = BoxSprite(chassis_shape, None)
    space.add(chassis_body, chassis_shape)

    # build wheel
    wheel_body, wheel_shape = make_wheel(wheel_surf)
    wheel_body.position = pymunk.Vec2d(chassis_body.position)
    wheel_shape.layers = layers
    wheel_shape.friction = record.wheel_friction

    motor = pymunk.SimpleMotor(chassis_body, wheel_body, 0.0)
    joint = pymunk.PivotJoint(chassis_body, wheel_body, (0, 0))

    sprite = CircleSprite(wheel_shape, wheel_surf)
    wheel_sprites.append(sprite)
    motors.append(motor)
    space.add(wheel_body, wheel_shape, motor, joint)

    kart = Kart(record)
    kart.chassis = chassis_sprite
    kart.wheels = wheel_sprites
    kart.motors = motors

    return kart
