import wallet
import transaction
import tx_validator
import serializer
import binascii
import codecs
import pending_pool
import cmd
import requests
import script
import utxo_set as utxo
from hashlib import sha256
import blockcypher
import config as cnf

API_KEY = "6f7e01bc443c48b985918a96cbc3b85b"
PORT = None

GREEN = "\033[1;32;40m"
BLUE = "\033[1;34;40m"
YELLOW = "\033[1;33;40m"
WHITE = "\033[1;37;40m"
RED = "\033[1;31;40m"
EOF = "\033[0m"

def generate_private(private_key):
	if private_key == 0:
		private_key = wallet.get_private_key()
	wif_key = wallet.convert_to_WIF(private_key)
	bitcoin_address = wallet.get_bitcoin_address(private_key)
	f = open('public_address', 'a')
	f.write(bitcoin_address + "\n")
	print(YELLOW + "Your public address is: " + EOF + bitcoin_address + YELLOW + "\nYou can find it in the file address")
	print(YELLOW + "Your private key: " + EOF + private_key)
	print(YELLOW + "Your private key in wif format is: " + EOF)
	print(wif_key)
	print(RED + "Please keep it in secret!!!")
	return private_key

def import_command(arg):
	try:
		f = open(arg, 'r')
		read = f.read()
		if len(read) != 52:
			raise ImportError
		private_key = wallet.WIF_to_key(read)
		private_key = generate_private(private_key)
		return private_key
	except IOError:
		print(RED + "Usage:\timport /path/to/file/with/WIF/Private/Key")
	except ImportError:
		print(RED + "Wrong import key")

class Cli(cmd.Cmd):
	def __init__(self):
		cmd.Cmd.__init__(self)
		self.prompt = GREEN+"฿ "
		self.intro  = GREEN+"\t\tWelcome to the bitcoin wallet :)\n"+ BLUE +"How to use? Type 'help'."
		self.doc_header = YELLOW+"For detail information use 'help' command"
		self.transaction = 1
		self.swtransaction = 1
		self.private_key = '0'

	
	def do_new(self, args):
		"""Generating new private key and public key. Bitcoin is address to the file."""
		self.private_key = generate_private(0)
	
	def do_import(self, args):
		"""Import private key (import in a WIF)"""
		if len(args.split(' ')) == 1:
			self.private_key = import_command(args)
		else:
			print(RED + "Usage:\timport /path/to/file/with/WIF/Private/Key")

	def do_send(self, args):
		"""recipient address and amount"""
		if self.private_key == '0':
			print(RED + "Import private key firstly!")
			return

		args = args.split(' ')
		if len(args) == 2:
			self.transaction = wallet.send(args[0], int(args[1]), self.private_key, "Pitcoin")
			if self.transaction != None:
				print(self.transaction)
			else:
				print(RED + "Something went wrong.")
		else:
			print(RED + "Usage:\tsend recipient_address amount\n")

	def do_broadcast(self, args):
		""" broadcast - send POST request with serialized transaction data to
		web API of Pitcoin full node, which provide route /transaction/new.
		broadcast Testnet - send POST request with serialized transaction data to Testnet"""
		if self.transaction != 1:
			args = args.split()
			if len(args) > 0 and args[0] == "-t":
				check = blockcypher.pushtx(tx_hex = self.transaction, coin_symbol='btc-testnet', api_key = API_KEY)
			else:
				broadcast_command(self.transaction)
				self.transaction = 1
		else:
			print('Use command send before broadcast command!\n')

	def do_balance(self, args):
		""" return balance of address, transmit in parameter. Iterating for
		each blocks and each transactions and calculate balance, based on sender and
		recipient address (if its sender, there is subtraction, in otherwise its
		addition)"""
		args = args.split(' ')
		if (len(args) != 2):
			print(RED + "Usage:\nbalance [-p|-t] address")
			return
		if args[0] == '-t':
			utxo.get_balance(args[1])
		else:
			utxo_set = utxo.get_utxo_set("Pitcoin", args[1])
			if utxo_set == None:
				return
			balance = utxo.check_balance(utxo_set)
			print(YELLOW + "Your balance is\t" + str(balance))

	def get_data(self):
		data = {}
		data['transaction'] = self.transaction
		data['private_key'] = self.private_key

	def do_exit(self, args):
		"""exit"""
		print("\033[1;34;40m\nBye, have a nice day!")
		exit(0)
	
def get_current_private_key():
	print("Enter your private key:\t")
	private_key = input()
	if (len(private_key) != 64 and len(private_key) != 51):
		print(RED + "Invalid private key\n")
		exit(0)
	if len(private_key) != 64:
		private_key = wallet.WIF_to_key(private_key)
	return private_key


def sign_verify(private_key, message, sender, recipient, amount):
	sign_pub_key = wallet.sign(private_key, message)
	return sign_pub_key


def create_hash(sender, recipient, amount):
	message = transaction.Transaction(sender, recipient, amount)
	message = message.transaction_hash_calculate()
	return message

def broadcast_command(transaction):
	cnf.broadcast_to_friend(transaction, '/transaction/new')
	print("Successfuly broadcasted")

def main():
	PORT = cnf.getPortFromFile()
	cli = Cli()
	try:
		cli.cmdloop()
	except KeyboardInterrupt:
		print("\033[1;34;40mBye, have a nice day!")

if __name__ == '__main__':
	main()