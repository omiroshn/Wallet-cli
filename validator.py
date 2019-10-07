import merkle
import pending_pool as pp
import script
import serializer as sr
from copy import deepcopy
import json
import pickle
import miner_cli
import requests
import binascii
from hashlib import sha256
from ast import literal_eval


def consensus():
	nodes = pp.read_nodes_from_file("node")
	len_list = []
	dicti = {}
	for x in nodes:
		dicti = {}
		dicti["ip"] = x
		try:
			dicti["length"] = int(requests.get("http://" + x + "/chain/length").text)
		except:
			dicti["length"] = 0
		len_list.append(dicti)
	newlist = sorted(len_list, key=lambda k: k['length']) 
	if (newlist[-1]['ip'] != nodes[0]):
		req = requests.get("http://" + newlist[-1]['ip'] + "/chain")
		chain = req.text
		req = requests.get("http://" + newlist[-1]['ip'] + "/utxo")
		utxo = req.text
		pp.add_data(chain, 'blockchain.pickle')
		pp.add_data(utxo, 'utxo.pickle')


def check_reward_target(coinbase, port, block_hash):
	req = requests.get("http://" + port + "/chain")
	if req.text == "Something get wrong!\nYou have no chain":
		consensus()
		return False
	try:
		chain = json.loads(req.text)
	except:
		consensus()
		return False
	reward = int(chain['reward'])
	reward = reward * pow(10, 8)
	tx = sr.Deserializer.deserializer(coinbase, 1)
	if tx['outputs'][0]['Value'] > reward:
		return False
	target = int(chain['target'])
	if (int(block_hash, 16) > target):
		print("Invalid block_hash")
		return False
	return True

def get_last_block(port):
	req = requests.get("http://" + port + "/block/last")
	if  req.text == 'Something get wrong!\nYou have no chain':
		consensus()
		return False
	try:
		last_block = json.loads(req.text)
	except:
		return False
	return last_block

def block(block):
	block = block.to_dict(flat=False)
	nodes = pp.read_nodes_from_file()
	my_node = nodes[0]
	if check_reward_target(block['transactions'][0], my_node, block['hash'][0]) == False:
		return False
	last_block = get_last_block(my_node)
	if (last_block == False):
		return False
	if last_block['hash'] != block['previous_hash'][0]:
		consensus()
	if float(last_block['timestamp']) > float(block['timestamp'][0]):
		return False
	merkle_norm = binascii.hexlify(merkle.create_merkle_tree(block['transactions'])).decode('utf-8')
	if (merkle_norm != block['merkle'][0]):
		return False
	if (len(block['transactions']) > 1):
		txs = deepcopy(block['transactions'])
		i = 0
		for tx in txs:
			if i > 0:
				if script.is_it_valid(tx) == False:
					return False
			i += 1
	return True

def mining(do):
	try:
		fd = open('mine', 'w')
	except IOError:
		print("Something get wrong!")
		exit(0)
	fd.write(str(do))
