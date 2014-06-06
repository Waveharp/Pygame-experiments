"""
this file exists for py2exe on the windows platform
"""
import os

cwd = os.getcwd()
os.environ["PLATAKART_CONF_PATH"] = os.path.join(cwd, "config", "platakart.ini")
os.environ["PLATAKART_RESOURCE_PATH"] = os.path.join(cwd, "resources")
from platakart import __main__
