import psycopg2
import yaml

# Менеджер для работы с postgree
class PostgreeDBManager(object):
    def __init__(self, database, user, host='localhost', password=None):
        self.connect=psycopg2.connect(database=database, user=user,
                                      host=host, password=password)# Устанавливаем соединение с базой данных
        self.cursor=self.connect.cursor()
    def createTableAuthorization(self):
        self.cursor.execute('CREATE TABLE authoriz(id SERIAL PRIMARY KEY,'
                            'login CHAR(64),'
                            'password CHAR(64),'
                            'UNIQUE(login));')# Уникальный логин
        self.connect.commit()
    def insertIntoAutoriz(self, login, password): # Добавляем новых пользователей
        self.cursor.execute('INSERT INTO authoriz(login, password)'
                            'VALUES (%s, md5(%s))', (login, password))# Храним пароль в виде хеша
        self.connect.commit()
    def deleteLoginInAutoriz(self, login): # Удаление по логину
        self.cursor.execute('DELETE FROM authoriz WHERE login=%s', (login,))
        self.connect.commit()
    def selectAllInAutorz(self):
        self.cursor.execute('SELECT*FROM authoriz')
        self.connect.commit()
        return self.cursor.fetchall()
    def createTableUserDirectory(self):
        self.cursor.execute('CREATE TABLE userdirectory(id SERIAL PRIMARY KEY,'
                            'login CHAR(64),'
                            'directory CHAR(64),'
                            'UNIQUE(login));')
        self.connect.commit()
    def insertIntoUserDirectory(self, login, directory):
        self.cursor.execute('INSERT INTO userdirectory(login, directory)'
                            'VALUES (%s, %s)', (login, directory))
        self.connect.commit()
    def deleteLoginInUserDirectory(self, login): # Удаление по логину
        self.cursor.execute('DELETE FROM userdirectory WHERE login=%s', (login,))
        self.connect.commit()
    def selectAllInUserDirectory(self):
        self.cursor.execute('SELECT*FROM userdirectory')
        self.connect.commit()
        return self.cursor.fetchall()



if __name__ == "__main__":
    settings = yaml.load(open('settings.yaml'))
    db=PostgreeDBManager(database=settings['dataBase']['nameDB'], user=settings['dataBase']['admin'],
                             password=settings['dataBase']['password'])#db.createTableAuthorization()
    #db.insertIntoAutoriz('jane','norge')
    #db.deleteLoginInAutoriz('kai')
    #db.createTableUserDirectory()
    a=db.selectAllInUserDirectory()
    from pprint import pprint
    pprint(a)
