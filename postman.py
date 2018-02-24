import json
import threading
import settings
import hashlib
import sys
from utils import *
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib
import socket



def isAlive(point):
	if point is None:
		return False
	addr = point.getAddr()
	source = xmlrpclib.ServerProxy(addr)
	socket.setdefaulttimeout(settings.defaulttimeout)
	try:
		pulse = source.checkPulse()
		return True
	except:
		return False
