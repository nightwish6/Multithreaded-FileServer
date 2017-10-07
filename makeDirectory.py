import yaml
from os import makedirs, path
# Создает директорию пользователя и заносит информацию в базу данных
def makeDir(user, dir, database, admin, host='localhost', password=None):
    try:
        makedirs((path.expanduser('~') + '/' + dir + '/' + user))# Создаем дирикторию пользователя
    except FileExistsError:
        print('Dir already created')
    dirUser=path.expanduser('~') + '/' + dir + '/' + user
    from postrgeeDBManager import PostgreeDBManager
    from psycopg2 import ProgrammingError
    db=PostgreeDBManager(database=database, user=admin, host=host, password=password)
    try:
        db.insertIntoUserDirectory(user, dirUser)# Вносим в базу данных информацию о расположении директории пользователя
    except ProgrammingError:
        print('DataBase does not exist')



if __name__ == "__main__":
    settings=yaml.load(open('settings.yaml'))
    makeDir('anna', 'users', database=settings['dataBase']['nameDB'],
            admin=settings['dataBase']['admin'],
            password=settings['dataBase']['password'])


