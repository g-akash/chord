from settings import *
import hashlib


def isEmpty(key):
	if key is None:
		return True
	if key == '':
		return True

	return False

def getHash(key):
	if isEmpty(key):
		raise ValueError(key+" is empty or None")
		exit()
	hash = hashlib.sha256(key)
	return hash.hexdigest()


# returns true if value lies in interval (start,finish]. open on the side of start

def liesInside(start,finish,value):
	if finish>start:
		if value<=finish and value > start:
			return True
		else:
			return False

	elif finish < start:
		if value > start and value >= finish:
			return True
		elif value <= finish and value < start:
			return True
		else:
			return False
	else:
		return True

def getValue(key):
	settings.datalock.acquire()
	if key in settings.data:
		value = settings.data[key]
	else:
		value = None
	settings.datalock.release()
	return value

def deleteKey(key):
	settings.datalock.acquire()
	if key in settings.data:
		del settings.data[key]
	settings.datalock.release()
	return

def addKey(key,value):
	settings.datalock.acquire()
	settings.data[key]=value
	settings.datalock.release()
	return

