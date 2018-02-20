import threading




ip = ''
port = 0
key = ''
numSuccessors = 3
datalock = threading.Lock()
data = {}
successorlock = threading.Lock()
# declare successor and successorlist here
successor = None
successorList = []
predecessorlock = threading.Lock() 
predecessor = None


