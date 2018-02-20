import sys
import os
import threading
import time
import settings
from utils import *
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib

class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2','/')



def stabilize():
	while True:
		time.sleep(10)

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
	return successor


def getPredecessor():
	settings.predecessorlock.acquire()
	predecessor = settings.predecessor
	settings.predecessorlock.release()
	return predecessor


def addMe(predecessor):
	settings.predecessorlock.acquire()
	if settings.predecessor is None:
		settings.predecessor = predecessor
	else:
		start = settings.predecessor.key
		finish = settings.key
		if liesInside(start,finish,predecessor.key):
			settings.predecessor = predecessor
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
	if liesInside(start,finish,key):
		return successor
	else:
		settings.successorlock.acquire()
		addr = settings.successor.getAddr()
		settings.successorlock.release()
		next = xmlrpclib.ServerProxy(addr)
		print "placeholder"
		return next.findNode(key)
		# do the thing about rpc call here


def find(key):
	source = findNode(key)
	print source
	return "done"


def add(key,value):
	source = findNode(key)
	print source
	return True


def delete(key):
	source = findNode(key)
	print source
	return True






# current format or arguments my ip and port, contact ip and port
def main():
	settings.ip = sys.argv[1]
	settings.port = int(sys.argv[2])
	if len(sys.argv) == 5:
		successor = node(sys.argv[3],sys.argv[4])
		settings.successor = successor
	else:
		successor = node(sys.argv[1],sys.argv[2])
		settings.successor = successor
        settings.successorList = [settings.successor]
        
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
	server.serve_forever()

	# start the thread work here
	return

if __name__ == '__main__':
        if len(sys.argv)!=3 and len(sys.argv)!=5:
                print "please run using correct format"
                print "python server.py <selfip> <selfport> <targetip> <targetport>"
                exit()
	main()
