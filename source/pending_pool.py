import tx_validator as tx
import serializer
import pickle
import merkle
import json
import config
import os
import script
from copy import deepcopy
from ast import literal_eval

def database(transaction):
	try:
		with open('pool.pickle', 'rb') as f:
			last_data = pickle.load(f)
			f.close()
		new_data = transaction + '\n' + last_data
	except:
		new_data = transaction
	with open('pool.pickle', 'wb') as f:
		pickle.dump(new_data, f)
		f.close()
	return new_data


def get_data(name):
	try:
		with open(name, 'rb') as f:
	 		pending_data = pickle.load(f)
	 		if type(pending_data) is str:
	 			pending_data = literal_eval(pending_data)
	 		f.close()
	 		return pending_data
	except:
		return False

def get_data_sas(name):
	try:
		with open(name, 'rb') as f:
	 		pending_data = pickle.loads(f)
	 		f.close()
	 		return pending_data
	except:
		return False


def get_last_transactions(transactions, n):
	last_transaction = []
	if transactions.find('\n') == -1:
		if transactions == '\n':
			return ''
		last_transaction.append(transactions)
		return last_transaction
	arr = transactions.split('\n')
	j = len(arr)
	if (j < n):
		return arr
	i = 0
	for elem in arr:
		if i < 3:
			last_transaction.append(elem)
		else:
			break
		i += 1
	return last_transaction


def remove_used_transactions(remove_from, used_data):
	if remove_from.find('\n') != -1:
		remove_from = remove_from.split('\n')
		for elem in used_data:
			try:
				i = remove_from.index(elem)
				del remove_from[i]
			except:
				i = 0
		if len(remove_from) == 0:
			os.remove('pool.pickle')
	else:
		os.remove('pool.pickle')
	data = get_data('pool.pickle')
	if data != False:
		with open('pool.pickle', 'wb') as f:
			new_data = ''
			for elem in remove_from:
				if elem == '':
					os.remove('pool.pickle')
					return
				new_data += elem + '\n'
			pickle.dump(new_data, f)

def remove_from_pool(transaction):
	pass

def get_valid_transactions(n):
	last_transaction = []
	try:
		with open('pool.pickle', 'rb') as f:
			data = pickle.load(f)
			f.close()
	except:
		return '1'
	last_transaction = get_last_transactions(data, 3)
	if last_transaction == "":
		return '1'
	for transaction in last_transaction:
		tx = deepcopy(transaction)
		tx1 = deepcopy(transaction)
		if script.is_it_valid(tx) == False:			
			remove_from_pool(tx)
			get_valid_transactions(n)
		else:
			if (tx1 != ''):
				script.work_with_utxo(tx1)
	remove_used_transactions(data, last_transaction)
	return last_transaction


def read_nodes_from_file(node = "node"):
	try:
		fd = open(node, 'r')
		ret = fd.readlines()
		fd.close()
		nodes = []
		for x in ret:
			nodes.append(x.replace("\n", ""))
		return(nodes)
	except IOError:
		print("Can't read from a node file")
		return (False)


def add_node_to_file(node):
	# print(node)
	try:
		fd = open("node", 'a')
		fd.write(str(node) + '\n')
		fd.close()
	except IOError:
		print("Can't write to node file")


def add_data(data, name):
	# data = json.dumps(data
	try:		
		with open(name, 'wb') as f:
	 		pickle.dump(data, f)
	 		f.close()
	except IOError as e:
		print("fail to open file %s" %name)


def pool(transaction):
	if valid.validation(transaction) == False:
		print("Transaction is not valid")
	else:
		transactions = database(transaction)
		# last_transaction = get_last_transactions(transactions)
		# return last_transaction
