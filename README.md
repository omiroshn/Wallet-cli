# how to install virtual env:
```
brew install python3
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
# algorithm to start the project:
1) запускаем python3 source/wallet_cli.py
2) запускается wallet cli, в котором есть такие команды:
3) help -> показать все доступные команды

4) нажимаем `new`, которая генерирует нам новый адресс
4) записываем публичный адресс куда-то на листочек, позже мы будем на него скидывать деньги
4) нажимаем еще раз `new`
4) записывает приватный ключ в wif формате в файлик `minerkey`
4) там хранится ключ майнера

4) открываем новое окно терминала
4) source venv/bin/activate
4) python3 source/miner_cli.py

4) открываем новое окно терминала
4) source venv/bin/activate
4) запускаем сервер
4) python3 source/server_commands.py

4) возвращаемся на второе окно с miner_cli
4) пишем `mine`
4) ждем пару секунд
4) ctrl+c

4) возвращаемся на первое окно с wallet_cli
4) пишем balance -p свой последний адресс

4) берем адрес который мы сохранили
4) send mzcdjD75QVbPAZEtq6J6tbHQmnCRUXrwmn 10000
4) оправляем 10 000 сатоши

4) broadcast

4) если сейчас проверить баланс, то он будет 0
4) майним `(mine)`

4) проверяем баланс и все деньги на месте!
