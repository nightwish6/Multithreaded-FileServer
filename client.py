import socket
import json
import sys
import os


class Client(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#Создаем сокет: IpV4 TCP
    def connect(self, ip, port):
        try: self.sock.connect((ip, port))#Устанавливаем соединение с сервером
        except ConnectionRefusedError:
            print('Connection error')
        else:
            self.response = self.sock.recv(1024)
            print(self.response.decode('utf-8'))#Получаем ответ от сервера
            self.authorization()
            self.showUserDir()
            self.sendFile()
        finally:
            self.sock.close()
    def authorization(self):# Авторизация пользователя, логин и пароль(захешированный) находятся в бд PostGree
        login=input('Login: ')
        password=input('Password: ')
        self.sock.send(bytes((json.dumps((login, password)).encode('utf-8'))))
    def showUserDir(self):
        response=self.sock.recv(1024).decode('utf-8')# Получаем ответ от сервера
        if response=='Wrong login or password':
            print(response)
            self.sock.close()
            sys.exit()
        else:
            try: userTree=json.loads(response)# В ответе мы получаем либо дерево каталогов пользователя, либо простой ответ, типа str
            except json.decoder.JSONDecodeError:
                if response=='User does not have a directory, contact your administrator':
                    print(response)
                    self.sock.close()
                    sys.exit()
            else:
                print('There are following files in your directory: ')
                for dir, folders, files in userTree: # Отображаем файлы из каталога
                    print(dir, folders, files)
    def sendFile(self): #Отправка файла на сервер
        fileName=input('File: ').strip()
        try: file=open(fileName, 'rb')
        except FileNotFoundError:
            print('No such file or directory\n'
                  'Specify the full path to the file')
            self.sendFile()
        else:
            self.sock.send(bytes(os.path.basename(fileName).encode('utf-8')))# Отправляем имя файла на сервер
            while True:
                buffer = file.read(1024)# Читаем фаил и отправляем TCP - пакетами
                if not buffer:
                    break
                self.sock.sendall(bytes(buffer))
            self.sock.shutdown(socket.SHUT_WR)# Чтобы подтвердить серверу, что фаил полностью отправлен, выключаем клиентский сокет и
            response = self.sock.recv(1024).decode("utf-8")# SHUT_WR, запрещаем отправку данных, затем вновь прослушиваем сокет.
            print(response)
        finally:
            self.sock.close()# Закрываем соединение





if __name__ == "__main__":
    cl1 = Client()
    cl1.connect('127.0.0.1', 56000)

