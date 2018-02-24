import sys
import os
import threading
import time
import settings
from utils import *
from postman import *
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib
import threading
import socket

class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2','/')

# function which keeps on running to balance the successor list and predecessor
def stabilize():
	while True:
		time.sleep(2)	
		successor = None
		settings.successorlistlock.acquire()
		currSuccList = settings.successorList
		settings.successorlistlock.release()
		print currSuccList[0].ip,currSuccList[0].port
		for succ in currSuccList:
			if succ is None:
				continue
			addr = succ.getAddr()
			source = xmlrpclib.ServerProxy(addr)
			try:
				actualPred = source.getPredecessor()
				successor = succ
				settings.successorlock.acquire()
				settings.successor = successor
				settings.successorlock.release()
				break
			except:
				print "could not connect to address",addr
				continue
			
		if successor is None:
			print "successor is None. Exiting Now"
			exit()
		if actualPred == "":
			actualPred = node(settings.ip,settings.port)
			source.setPredecessor(actualPred)
		else:
			actualPred = node(actualPred['ip'],actualPred['port'])
			
		if liesInside(settings.key,successor.getKey(),actualPred.getKey()) and isAlive(actualPred):
			settings.successorlock.acquire()
			settings.successor = actualPred
			settings.successorlock.release()
		else:
			source.setPredecessor(node(settings.ip,settings.port))
		
		#successor is finalized at this point
		settings.successorlock.acquire()
		successor = settings.successor
		newSuccessorList = [successor]
		settings.successorlock.release()
		
		
		# do it after we have finalized the successor
		for i in range(settings.numSuccessors-1):
			source = xmlrpclib.ServerProxy(newSuccessorList[-1].getAddr())
			try:
				succ = source.getSuccessor()
			except:
				break
			if succ == "":
				break
			succ = node(succ['ip'],succ['port'])
			newSuccessorList.append(succ)
		settings.successorlistlock.acquire()
		settings.successorList = newSuccessorList
		settings.successorlistlock.release()
		for var in newSuccessorList:
			print var,
		print ""



#~ def stabilize():
	#~ while True:
		#~ time.sleep(10)
		#~ print "running stabilize"
		#~ settings.successorlock.acquire()
		#~ successor = settings.successor
		#~ addr  = settings.successor.getAddr()
		#~ settings.successorlock.release()
		#~ source = xmlrpclib.ServerProxy(addr)
		#~ actualPred = source.getPredecessor()
		#~ if actualPred == "":
			#~ print "obtained empty predecessor. Asking successor to set myself as predecessor."
			#~ source.setPredecessor(node(settings.ip,settings.port))
			#~ actualPred = node(settings.ip,settings.port)
			#~ print "succ",settings.successor.ip, settings.successor.port
			#~ continue
				
		#~ if liesInside(settings.key,successor.getKey(),actualPred['key']):
			#~ settings.successorlock.acquire()
			#~ settings.successor = node(actualPred['ip'],int(actualPred['port']))
			#~ settings.successorlock.release()
		#~ else:
			#~ source.setPredecessor(node(settings.ip,settings.port))
		#~ if settings.predecessor is not None:
			#~ print "pred",settings.predecessor.ip, settings.predecessor.port
		#~ else:
			#~ print "predecessor is none"
		
		#~ print "succ",settings.successor.ip, settings.successor.port
	#~ print "stabilize finished due to some reason"
	#~ return



# these functions are called when we know that key has to reside on this node only

# function to insert key into the database
def keyInsert(key,value):
	addKey(key,value)
	return True


# function to delete key from the database
def keyDelete(key):
	deleteKey(key)
	return True


#function to get value of a key from database
def keyFind(key):
	value = getValue(key)
	return value



# function to get successorlist of this node

def getSuccessorList():
	settings.successorlock.acquire()
	successorList = settings.successorList[:]
	settings.successorlock.release()
	return successorList

# function to get the successot of this node

def getSuccessor():
	settings.successorlock.acquire()
	successor = settings.successor
	settings.successorlock.release()
	if successor is None:
		return ""
	print successor
	return successor

# function to get the predecessor of this node

def getPredecessor():
	settings.predecessorlock.acquire()
	predecessor = settings.predecessor
	settings.predecessorlock.release()
	if predecessor is None:
		return ""
	return predecessor
 
# function to set predecessor of this node

def setPredecessor(predecessor):
	settings.predecessorlock.acquire()
	settings.predecessor = node(predecessor['ip'],predecessor['port'])
	settings.predecessorlock.release()
	return ""


# node requesting this node to add me as the predecessor

def addMe(predecessor):
	settings.predecessorlock.acquire()
	if settings.predecessor is None:
		settings.predecessor = node(predecessor['ip'],predecessor['port'])
	else:
		start = settings.predecessor.key
		finish = settings.key
		if liesInside(start,finish,predecessor['key']):
			settings.predecessor = node(predecessor['ip'],predecessor['port'])
	settings.predecessorlock.release()
	curr = node(settings.ip,settings.port)
	return curr
		
			

# find the node which can possibly hold this key in the network 
def findNode(key):
	if key is None:
		return None
	settings.successorlock.acquire()
	successor = settings.successor
	finish = settings.successor.getKey()
	settings.successorlock.release()
	start = settings.key
	if liesInside(start,finish,key)==True:
		return successor
	else:
		addr = successor.getAddr()
		next = xmlrpclib.ServerProxy(addr)
		return next.findNode(key)

# client side interface function for find key
def find(key):
	source = findNode(key)
	addr = makeAddr(source['ip'],int(source['port']))
	source = xmlrpclib.ServerProxy(addr)
	return source.keyFind(key)

# client side interface function for add key,value pair to database

def add(key,value):
	source = findNode(key)
	addr = makeAddr(source['ip'],int(source['port']))
	source = xmlrpclib.ServerProxy(addr)
	return source.keyAdd(key,value)

# client side interface function for deleting key from database

def delete(key):
	source = findNode(key)
	addr = makeAddr(source['ip'],int(source['port']))
	source = xmlrpclib.ServerProxy(addr)
	return source.keyDelete(key)


# function to check if the node is still alive and serving

def checkPulse():
	return True





# current format or arguments my ip and port, contact ip and port
# based on the type of call either set itself as the successor or find successor first using the address given
# and then ask that node to add me

# also start serving from this node
def main():
	socket.setdefaulttimeout(settings.defaulttimeout)
	settings.ip = sys.argv[1]
	settings.port = int(sys.argv[2])
	settings.key = getHash(settings.ip+str(settings.port))
	slf = node(sys.argv[1],sys.argv[2])
	if len(sys.argv) == 5:
		addr = makeAddr(sys.argv[3],sys.argv[4])
		source = xmlrpclib.ServerProxy(addr)
		succ = source.findNode(settings.key)
		successor = node(succ['ip'],succ['port'])
		settings.successor = successor
		settings.successorList = [settings.successor]
		addr = successor.getAddr()
		source = xmlrpclib.ServerProxy(addr)
		myself = node(settings.ip,settings.port)
		succ = source.addMe(myself)
	else:
		successor = node(sys.argv[1],sys.argv[2])
		settings.successor = successor

		settings.successorList = [settings.successor]
		print len(settings.successorList)
		print settings.successorList
		print
		
	threading.Thread(target=stabilize).start()
	server = SimpleXMLRPCServer((settings.ip,settings.port),requestHandler=RequestHandler)
	server.register_introspection_functions()
	server.register_function(keyInsert,'keyInsert')
	server.register_function(keyFind,'keyFind')
	server.register_function(keyDelete,'keyDelete')
	server.register_function(getSuccessor,'getSuccessor')
	server.register_function(getSuccessorList,'getSuccessorList')
	server.register_function(getPredecessor,'getPredecessor')
	server.register_function(addMe,'addMe')
	server.register_function(findNode,'findNode')
	server.register_function(find,'find')
	server.register_function(add,'add')
	server.register_function(delete,'delete')
	server.register_function(setPredecessor,'setPredecessor')
	server.register_function(checkPulse,'checkPulse')
	server.serve_forever()
	# start the thread work here
	return

if __name__ == '__main__':
	if len(sys.argv)!=3 and len(sys.argv)!=5:
		print "please run using correct format"
		print "python server.py <selfip> <selfport> <targetip> <targetport>"
		exit()
	main()
