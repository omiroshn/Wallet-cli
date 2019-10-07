import wallet
import binascii
import miner_cli
import wallet_cli








def createKeysAndAddresses():
	privkey_1 = wallet.get_private_key()
	privkey_2 = wallet.get_private_key()
	privkey_3 = wallet.get_private_key()
	print("Privkey 1:",privkey_1)
	print("Privkey 2:",privkey_2)
	print("Privkey 3:",privkey_3)

	wif1 = wallet.convert_to_WIF(privkey_1).decode()
	wif2 = wallet.convert_to_WIF(privkey_2).decode()
	wif3 = wallet.convert_to_WIF(privkey_3).decode()
	print("WIF key 1:",wif1)
	print("WIF key 2:",wif2)
	print("WIF key 3:",wif3)

	with open('minerkey', 'w') as f:
		f.write(wif1)
	with open('wif1', 'w') as f:
		f.write(wif1)
	with open('wif2', 'w') as f:
		f.write(wif2)
	with open('wif3', 'w') as f:
		f.write(wif3)

	pubkeys = []
	pubkeys.append(wallet.get_public_key(privkey_1))
	pubkeys.append(wallet.get_public_key(privkey_2))
	pubkeys.append(wallet.get_public_key(privkey_3))
	return pubkeys




def premine_mode(pubkeys, minercli):
	addr1 = wallet.get_bitcoin_address_from_public_key(pubkeys[0])
	addr2 = wallet.get_bitcoin_address_from_public_key(pubkeys[1])
	addr3 = wallet.get_bitcoin_address_from_public_key(pubkeys[2])

	with open('addr1', 'w') as f:
		f.write(addr1)
	with open('addr2', 'w') as f:
		f.write(addr2)
	with open('addr3', 'w') as f:
		f.write(addr3)

	walletcli = wallet_cli.Cli()
	# minercli = miner_cli.Cli()

	for i in range(2):
		minercli.mine()

	print("-----")
	walletcli.do_import('wif1')
	print("-----")
	walletcli.do_send('-p ' + addr1 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr2 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr3 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr1 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr2 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr3 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr1 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr2 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr3 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr1 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr2 + ' ' + str(1000000))
	walletcli.do_broadcast("")
	walletcli.do_send('-p ' + addr3 + ' ' + str(1000000))
	walletcli.do_broadcast("")

	for i in range(8):
		minercli.mine()
