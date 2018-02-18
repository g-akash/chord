import threading

class node:
	def __init__(self,ip,port):
		self.ip = ip
		self.port = port

	def getIp():
		return self.ip

	def getPort():
		return self.port

	def setIp(ip):
		self.ip = ip
		return

	def setPort(port):
		self.port = port
		return



ip = ''
port = 0
numSuccessors = 3
datalock = threading.Lock()
data = {}
successorlock = threading.Lock()
# declare successor and successorlist here
successor = None
successorList = []


