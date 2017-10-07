import socketserver
import threading
import json
import hashlib
import os
import logging
import yaml
from postrgeeDBManager import PostgreeDBManager

class FileServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        logging.info('Connected to the server: {}'.format(self.client_address))
        currentThread=threading.current_thread()# Возвращает текущий объект-поток, т.е. соответствующий потоку управления, который вызвал эту функцию
        response='Connected to the File server successfully\nYour Thread: %s'%(currentThread.getName())
        self.request.send(bytes(response.encode('utf-8')))
        self.authorization()# Авторизация пользователя
    def authorization(self):
        self.data=json.loads(self.request.recv(1024).decode('utf-8'))
        logging.info('The server processes the client {} login and password'.format(self.client_address))
        hash=hashlib.md5(self.data[1].encode('utf-8'))
        users=server.dataBase.selectAllInAutorz()# Обращаемся на сервер, к экземпляру класса postgreeDBManager
        for user in users:
            if user[1].strip()==self.data[0] and user[2].strip()==hash.hexdigest():# Сравнение хешей паролей
                logging.info('The clients {} authorization was successful, the client is recognized as {}'.format(self.client_address, self.data[0]))
                self.showDirUser()
                break
        else:
            self.request.send(bytes('Wrong login or password'.encode('utf-8')))
            logging.warning('Incorrect login or password of the user, the server closes the connection with the client {} '.format(self.client_address))
            server.close_request()
    def showDirUser(self):
        self.dirs=server.dataBase.selectAllInUserDirectory()# Отправляем запрос в базу данных для поиска директории пользователя
        for dir in self.dirs:
            if dir[1].strip()==self.data[0]:
                self.tree=[d for d in os.walk(dir[2].strip())]# Создаем дерево каталогов пользователя на сервере
                logging.info('The server created the user {} directory tree: {}'.format((self.client_address, self.data[0]), self.tree))
                self.request.send(bytes((json.dumps(self.tree).encode('utf-8'))))# Отправляем пользователю данные
                self.loadFile()
                break
        else:
            self.request.send(bytes('User does not have a directory, contact your administrator'.encode('utf-8')))
            logging.warning('User {} does not have a directory, the server closes the connection'.format((self.client_address, self.data[0])))
            server.close_request()
    def loadFile(self):
        fileName=self.request.recv(1024).decode('utf-8')
        logging.info('User {} uploads the file {} to the directory {}'.format((self.client_address, self.data[0]), fileName, self.tree))
        file=open(self.tree[0][0]+'/'+fileName, 'wb') # Подготавливаем фаил для записи в директорию пользователя
        while True:
            data=self.request.recv(1024)# Получаем данные от клиента
            if not data:
                file.close()
                break
            file.write(data)# Записываем данные в фаил
        logging.info('Uploading a user {} file {} was successful'.format((self.client_address, self.data[0]), fileName))
        self.request.send(bytes('File uploaded successfully'.encode('utf-8')))# Подтверждение что фаил доставлен
        logging.info('The server closes the connection with the user {} '.format((self.client_address, self.data[0])))
        server.close_request()# Закрываем соединение



class FileServer(socketserver.ThreadingTCPServer, socketserver.TCPServer):
    def setup(self, dataBase, loggerConfig, loggerFile):
        self.dataBase=dataBase
        logging.basicConfig(format=loggerConfig, level=logging.DEBUG, filename=loggerFile)# Настраиваем логгер





if __name__ == "__main__":
    settings = yaml.load(open('settings.yaml'))
    db=PostgreeDBManager(database=settings['dataBase']['nameDB'], user=settings['dataBase']['admin'],
                         password=settings['dataBase']['password'])
    server=FileServer(("127.0.0.1", 56000), FileServerHandler)
    server.setup(dataBase=db, loggerConfig=settings['logger']['loggerConfig'],
                 loggerFile=settings['logger']['loggerFile'])
    serverThread=threading.Thread(target=server.serve_forever)# Запускаем поток с сервером, для каждого нового запроса этот поток запустит еще один поток
    serverThread.setDaemon(False)
    serverThread.start()


