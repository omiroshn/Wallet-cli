import cmd
import os
import blockchain
import server_commands
import pending_pool as pp
import json
import argparse
import requests
import premine
import config as cnf

PORT = None

class Cli(cmd.Cmd):
	def __init__(self, is_premine = 0):
		cmd.Cmd.__init__(self)
		self.prompt = "฿ "
		self.intro  = "\t\tWelcome to the miner cli\nHow to use? 'help'!!"
		self.doc_header ="For detail information use 'help _command_')"
		self.blockchain = pp.get_data("blockchain.pickle")
		if (self.blockchain == False or is_premine == True):
			try:
				os.remove("utxo.pickle")
			except:
				pass
			self.blockchain = blockchain.Blockchain()
			if is_premine == True:
				print("PREMINE IS ON")
				pubkeys = premine.createKeysAndAddresses()
			if self.blockchain.genesis_block() == False:
				exit(1)
			if is_premine == True:
				premine.premine_mode(pubkeys, self)

		# self.mine = True
		# self.utxo = utxo_set.Utxo_pool()

	def mine(self):
		chain = self.blockchain.chain
		self.blockchain.mine(chain[0].hash)
		print("New block hash", self.blockchain.chain[0].hash)

	def do_mine(self, args):
		"""mine - start mining process. Mine block with getting transactions 
		from pending pool, adding coinbase transaction with miner address from a file,
		calculation parameters like merkle root, hash and saving block in chain"""

		# self.do_consensus(args)
		while True:
			try:
				fd = open('mine', 'r')
			except:
				print("Mining has been stoped(((")
				break
			m = fd.readline()
			if m == '3':
				print("In file mine is '3', so it's time to do something else!\nFor starting mine process, please write in file mine '1' and start command mine")
				return
			while m == '1':
				self.mine()
				m = '0'
				fd.close()
	
	def do_exit(self, args):
		"""exit"""
		print("Bye, have a nice day!")
		exit(0)

	def do_add_node(self, args):
		"""add_node - adding node to nodes list of Blockchain (based on received
		parameter in URL format without scheme)"""
		if len(args.split(' ')) == 1:
			if self.blockchain.add_node(args) == 1:
				print("Node sucsessfuly added!")
			else:
				print("Unvalid node, please check it and use this command again")
		else:
			print("usage\tadd_node ip:port")
	
def main():
	PORT = cnf.getPortFromFile()
	print("Port = ", PORT)
	parser = argparse.ArgumentParser(description='Miner client, you know.You can see help menu after entering miner_cli and typing "help"')
	parser.add_argument('-p', dest='feature', action='store_true', help='activates premine mode')
	options = parser.parse_args()
	cli = Cli(options.feature)
	try:
		cli.cmdloop()
	except KeyboardInterrupt:
		print("\nBye, have a nice day!")

if __name__ == '__main__':
	main()
