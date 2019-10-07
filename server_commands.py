import sys
import validator
import json
import utxo_set
import config
import pending_pool
import pickle
from flask import (
    Flask,
    request
)

app = Flask(__name__)


@app.route('/transaction/new', methods=['POST'])
def submit_tx():
    if request.method == 'POST':
        next_transaction = request.get_data()
        next_transaction = next_transaction.decode('utf-8')
        pending_pool.database(next_transaction)
        return(str(next_transaction))


@app.route('/transaction/pending', methods=['GET'])
def pending_transaction():
    if request.method == 'GET':
        data = pending_pool.get_data('pool.pickle')
        if data != False:
            return str(data)
        else:
            return("Something get wrong!\nYou have no transaction in pool")


@app.route('/chain', methods=['GET'])
def get_chain():
    if request.method == 'GET':
        data = pending_pool.get_data('blockchain.pickle')
        if data != False:
            if (type(data) == str):
                data = json.loads(data)
            return str(data)
        else:
            return("Something get wrong!\nYou have no chain")


@app.route('/nodes', methods=['GET'])
def list_of_nodes():
    if request.method == 'GET':
        data = pending_pool.read_nodes_from_file('node')
        ret = ''.join(data)
        if data != False:
            return (ret)
        else:
            return("Something get wrong!\nYou have no nodes")


@app.route('/chain/length', methods=['GET'])
def chain_length():
    if request.method == 'GET':
        data = pending_pool.get_data('blockchain.pickle')
    if data != False:
        if type(data) is dict:
            lens = str(data['chain'][0]['height'])
        else:
            lens = str(data.chain[0].height)
        return lens
    else:
        return("0")


@app.route('/block/last', methods=['GET'])
def last_block():
    if request.method == 'GET':
        data = pending_pool.get_data('blockchain.pickle')
        if data != False:
            if type(data) is dict:
                block = data['chain'][0]
            else:
                block = data.chain[0]
            return str(block)
        else:
            return("Something get wrong!\nYou have no chain")


@app.route('/block', methods=['GET'])
def block_height():
    if request.method == 'GET':
        height = str(request.args.get('height'))
        data = pending_pool.get_data('blockchain.pickle')
        if data != False:
            i = len(data.chain) - 1
            while(i >= 0):
                if (int(data.chain[i].height) == int(height)):
                    return str(data.chain[i])
                i -= 1
            return "No such block!"
        else:
            return "There no chain data!"


@app.route('/balance', methods=['GET'])
def get_balance():
    if request.method == 'GET':
        addr = str(request.args.get('addr'))
        setik = utxo_set.get_utxo_set("Pitcoin", addr)
        balance = utxo_set.check_balance(setik)
        return('<h1>Your balance is <font color="red">' + str(balance) + '</font> satoshi</h1>')


@app.route('/utxo', methods=['GET'])
def utxo():
    if request.method == 'GET':
        data = pending_pool.get_data('utxo.pickle')
        if data != False:
            return str(data)
        else:
            return("Something get wrong!\nYou have no utxo in pool")


@app.route('/block/new', methods=['POST'])
def receive_new_block():
    if request.method == 'POST':
        validator.mining(0)
        block = request.form
        if validator.block(block) == True:
            validator.consensus()
        validator.mining(1)
        return "OK"
    return ("OK")


@app.route('/getDifficulty', methods=['GET'])
def get_difficulty():
    if request.method == 'GET':
        data = pending_pool.get_data('blockchain.pickle')
        if data != False:
            diff = data.diff
            return str(diff)
        else:
            return("Something get wrong!\nYou have no chain")


def main():
    ip = pending_pool.read_nodes_from_file()
    if ip == False:
        PORT = input("Choose port\n")
        try:
            val = int(PORT)
            try:
                fd = open("port.txt", 'w')
                fd.write(PORT)
                fd.close()
                pending_pool.add_node_to_file("0.0.0.0:" + PORT)
                app.run(host='0.0.0.0', port=PORT, debug=False)
                print("!!!Server port was saved in a file port.txt!!!")
            except IOError:
                print("IOError")
        except (ValueError, PermissionError, OverflowError) as e:
            print("Invalid port, stupid")
    else:
        app.run(host=ip[0][:7], port=ip[0][8:13], debug=False)


if __name__ == '__main__':
    main()
