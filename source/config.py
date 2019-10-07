import requests
import pickle
import json
import block
import pending_pool as pp

def broadcast_to_friend(data, where):
	nodes = [] 
	nodes = pp.read_nodes_from_file()
	if nodes == False:
		print("Please, firstly run a server!")
		exit()
	if (type(data) is block.Block):
		a = data.__dict__
		data = a
	for node in nodes:
		try:
			req = requests.post("http://" + node + where, data = data)
		except:
			print("Node has no connection")

def getPortFromFile(file = "port.txt"):
	try:
		fd = open(file, 'r')
		return (fd.read())
	except IOError:
		print("can't read file %s" % file)