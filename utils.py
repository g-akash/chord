import settings
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
		value = ""
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


class node:
	def __init__(self,ip,port):
		if ip is None or port is None:
			raise ValueError(ip+" or "+str(port)+" is None")
			exit()
		self.ip = ip
		self.port = port
		self.setkey()


	def __str__(self):
		ans = "ip:"+self.ip+",port:"+str(self.port)+",key:"+self.key
		return ans

	def setkey(self):
		self.key = getHash(self.ip+str(self.port))

	def getIp(self):
		return self.ip

	def getPort(self):
		return self.port

	def getKey(self):
		return self.key

	def getAddr(self):
		return 'http://'+self.ip+":"+str(self.port)

	def setIp(self,ip):
		if ip is None:
			return
		self.ip = ip
		self.setkey()
		return

	def setPort(self,port):
		if port is None:
			return
		self.port = port
		self.setkey()
		return




def makeAddr(ip,port):
        addr = "http://"+ip+":"+str(port)
        return addr
