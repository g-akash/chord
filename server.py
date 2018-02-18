import sys
import os
import threading
import time
from settings import *



def stabilize():
	while True:
		time.sleep(10)

	return






# current format or arguments my ip and port, contact ip and port
def main():
	settings.ip = sys.argv[0]
	settings.port = sys.argv[1]
	if len(sys.argv) == 4:
		successor = node(sys.argv[2],sys.argv[3])
		settings.successor = successor
	else:
		successor = node(sys.argv[0],sys.argv[1])
		settings.successor = successor


	settings.successorList = []

	# start the thread work here
	return

if __name__ == '__main__':
	main()