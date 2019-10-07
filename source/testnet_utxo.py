import blockcypher
import tx_validator as tx

def get_balance(address):
	if tx.availabilyty_of_address(address) == False:
		print ("Address is invalid!")
		return
	satoshis = blockcypher.get_total_balance(address, coin_symbol='btc-testnet')
	print (str(blockcypher.from_satoshis(satoshis, 'btc')) + " btc")