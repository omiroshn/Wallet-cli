import config
import codecs
import wallet

class Serializer():
	@staticmethod
	def serializer(transaction):
		if len(transaction) < 7:
			transaction['marker'] = ''
			transaction['flag'] = ''
			transaction['witness'] = []
			transaction['witness'].append('')
		inputs_concat = '0'
		for elem in transaction['input']:
			inputs_concat += elem.input_concat()
		inputs_concat = inputs_concat[1:]
		outputs_concat = '0'
		for elem in transaction['output']:
			outputs_concat += elem.output_concat()
		witness_concat = ''
		for elem in transaction['witness']:
			witness_concat += elem
		outputs_concat = outputs_concat[1:]
		ser_trans = transaction['version'] + transaction['marker'] + transaction['flag'] + transaction['input_count'] + inputs_concat + transaction['output_count'] + outputs_concat + transaction['locktime']
		return ser_trans

def check_par(par):
	i = 0
	while par[i] == '0':
		if len(par) == 1:
			break
		par = par[1:]
	return par

def return_to_normal_form(data):
	return check_par(codecs.encode(codecs.decode(data, 'hex')[::-1], 'hex').decode())

class Deserializer():
	@staticmethod
	def deserializer(string, coinbase):
		transaction = {}
		version = string[:8]
		transaction['version'] = check_par(return_to_normal_form(version))
		transaction['input_count'] = check_par(string[8:10])
		transaction['inputs'] = []
		if coinbase != 1:
			j = 10
			for elem in range(int(transaction['input_count'], 16)):
				inputiki = {}
				i = j
				j = i + 64
				inputiki['TXID'] = return_to_normal_form(string[i:j])
				i = j
				j = i + 8
				inputiki['VOUT'] = check_par(return_to_normal_form(string[i:j]))
				i = j
				j = i + 2
				inputiki['ScriptSigSize'] = string[i:j]
				i = j
				j = i + (int(inputiki['ScriptSigSize'], 16) * 2)
				inputiki['ScriptSig'] = string[i:j]
				i = j
				j = i + 8
				inputiki['Sequence'] = string[i:j]
				transaction['inputs'].append(inputiki)
				i = i + 8
		else:
			i = 230
		j = i + 2
		transaction['output_count'] = string[i:j]
		transaction['outputs'] = []
		for elem in range(int(transaction['output_count'], 16)):
			output = {}
			i = j
			j = i + 16
			output['Value'] = int(check_par(return_to_normal_form(string[i:j])), 16)
			i = j
			j = i + 2
			output['SPKS'] = string[i:j]
			i = j
			j = i + (int(output['SPKS'], 16) * 2)
			output['SPK'] = string[i:j]
			encrypt_key = '6F' + output['SPK'][6:-4]
			output['address'] = wallet.base58_my(encrypt_key + wallet.get_checksum(encrypt_key))
			transaction['outputs'].append(output)
		i = j
		j = i + 8
		transaction['locktime'] = string[i:j]
		return transaction 
