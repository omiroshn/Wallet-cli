import config
import json
import requests

address = 'mqpX83GLFpK4MABmMSgAQaVGg5CJAbaWGW'

resp = requests.get('https://testnet.blockchain.info/unspent?active=%s' % address)
utxo_set = json.loads(resp.text)["unspent_outputs"]

def get_balance(address):
	balance = 0
	resp = requests.get('https://testnet.blockchain.info/unspent?active=%s' % address)
	utxo_set = json.loads(resp.text)["unspent_outputs"]
	for utxo in utxo_set:
		


for utxo in utxo_set:
	print(utxo)
	# print("%s:%d - %ld Satoshis" % (utxo['tx_hash'], utxo['tx_output_n'], utxo['value']))

