# -*- coding: utf-8; -*-

from argparse import ArgumentParser
import logging
import os
import os.path

logger = logging.getLogger("platakart.__main__")

from platakart.config import save_config
from platakart.core import create_game

parser = ArgumentParser(prog="platakart", description="Platakart Racing!")

parser.add_argument(
    "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="WARNING", help="Verbosity of logging output")

args = parser.parse_args()

logging.basicConfig(
    level=getattr(logging, args.log_level),
    format="%(name)s:%(filename)s:%(lineno)d:%(levelname)s: %(message)s")


config_file_path = os.getenv("PLATAKART_CONF_PATH")

if config_file_path is None:
    home = os.path.expanduser("~")
    config_file_path = os.path.join(home, ".platakart", "platakart.ini")

try:
    logger.debug("PLATAKART_CONF_PATH env arg not defined")
    with open(config_file_path, "r"):
        pass
except:
    logger.debug("No config file found in home folder,"
                 "creating default config file. ")
    save_config(config_file_path, None)

control_config_path = os.path.join(
    os.path.split(config_file_path)[0], "controls.xml")

game = create_game(config_file_path, control_config_path)
game.main_loop()
