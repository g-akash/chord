import sys
import os
import threading
import time
import settings
from utils import *
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib
import threading

class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2','/')


def newStabilize():
	while True:
		time.sleep(10)
		print "running a loop of stabilize"		
		settings.successorlock.acquire()
		successor = settings.successor
		addr = successor.getAddr()
		settings.successorlock.release()
		source = xmlrpclib.ServerProxy(addr)
		actualPred = source.getPredcessor()
		if actualPred == "":
			print "obtained empty predecessor. Asking him to set me as predecessor"
			actualPred = node(settings.ip,settings.port)
			source.setPred(actualPred)
		else:
			actualPred = node(actualPred['ip'],actualPred['port'])
			
		if liesInside(settings.key,successor.getKey(),actualPred.getKey()):
			settings.successorlock.acquire()
			settings.successor = actualPred
			settings.successorlock.release()
		else:
			source.setPredecessor(node(settings.ip,settings.port))
		
		#successor is finalized at this point
		settings.successorlock.acquire()
		successor = settings.successor
		newSuccessorLock = [successor]
		settings.successorlock.release()
		
		
		# do it after we have finalized the successor
		for i in range(settings.numSuccessors-1):
			source = xmlrpclib.ServerProxy(newSuccessorList[-1].getAddr())
			succ = source.getSuccessor()
			if succ == "":
				break
			succ = node(succ['ip'],succ['port'])
			newSuccessorList.append(succ)
		settings.successorlistlock.acquire()
		settings.successorList = newSuccessorList
		settings.successorlistlock.release()
		


def stabilize():
	while True:
		time.sleep(10)
		print "running stabilize"
		settings.successorlock.acquire()
		successor = settings.successor
		addr  = settings.successor.getAddr()
		settings.successorlock.release()
		source = xmlrpclib.ServerProxy(addr)
		actualPred = source.getPredecessor()
		if actualPred == "":
			print "obtained empty predecessor. Asking successor to set myself as predecessor."
			source.setPredecessor(node(settings.ip,settings.port))
			actualPred = node(settings.ip,settings.port)
			print "succ",settings.successor.ip, settings.successor.port
			continue
				
		if liesInside(settings.key,successor.getKey(),actualPred['key']):
			settings.successorlock.acquire()
			settings.successor = node(actualPred['ip'],int(actualPred['port']))
			settings.successorlock.release()
		else:
			source.setPredecessor(node(settings.ip,settings.port))
		if settings.predecessor is not None:
			print "pred",settings.predecessor.ip, settings.predecessor.port
		else:
			print "predecessor is none"
		
		print "succ",settings.successor.ip, settings.successor.port
	print "stabilize finished due to some reason"
	return




def keyInsert(key,value):
	addKey(key,value)
	return True

def keyDelete(key):
	deleteKey(key)
	return True

def keyFind(key):
	value = getValue(key)
	return value




def getSuccessorList():
	settings.successorlock.acquire()
	successorList = settings.successorList[:]
	settings.successorlock.release()
	return successorList

def getSuccessor():
	settings.successorlock.acquire()
	successor = settings.successor
	settings.successorlock.release()
	if successor is None:
		return ""
	return successor


def getPredecessor():
	settings.predecessorlock.acquire()
	predecessor = settings.predecessor
	settings.predecessorlock.release()
	if predecessor is None:
		return ""
	return predecessor
 

def setPredecessor(predecessor):
	settings.predecessorlock.acquire()
	settings.predecessor = node(predecessor['ip'],predecessor['port'])
	settings.predecessorlock.release()
	return ""

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
		print "placeholder"
		return next.findNode(key)
		# do the thing about rpc call here


def find(key):
	source = findNode(key)
	addr = makeAddr(source['ip'],int(source['port']))
	source = xmlrpclib.ServerProxy(addr)
	return source.keyFind(key)


def add(key,value):
	source = findNode(key)
	addr = makeAddr(source['ip'],int(source['port']))
	source = xmlrpclib.ServerProxy(addr)
	return source.keyAdd(key,value)


def delete(key):
	source = findNode(key)
	addr = makeAddr(source['ip'],int(source['port']))
	source = xmlrpclib.ServerProxy(addr)
	return source.keyDelete(key)






# current format or arguments my ip and port, contact ip and port
def main():
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
		addr = successor.getAddr()
		source = xmlrpclib.ServerProxy(addr)
		myself = node(settings.ip,settings.port)
		succ = source.addMe(myself)
	else:
		successor = node(sys.argv[1],sys.argv[2])
		settings.successor = successor

		settings.successorList = [settings.successor]
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
	server.serve_forever()
		
	# start the thread work here
	return

if __name__ == '__main__':
	if len(sys.argv)!=3 and len(sys.argv)!=5:
		print "please run using correct format"
		print "python server.py <selfip> <selfport> <targetip> <targetport>"
		exit()
	main()
