import sqlite3

class Repository:

    def __init__(self, dbFile):
        """Инициализация соединения с БД"""
        self.conn = sqlite3.connect(dbFile)
        self.cursor = self.conn.cursor()

    def userExists(self, user_id):
        """Проверяем, есть ли юзер в БД"""
        result = self.cursor.execute("SELECT 'id' FROM 'users' WHERE 'userId' = ?", (user_id,))
        return bool(len(result.fetchall()))

    def getUserId(self, user_id):
        """Получаем ID юзера в из БД по его userId в Телеграмме"""
        result = self.cursor.execute("SELECT 'id' FROM 'users' WHERE 'userId' = ?", (user_id,))
        return result.fetchone()[0]

    def addUser(self, user_id):
        """Добавляем юзера в БД"""
        self.cursor.execute("INSERT INTO 'users' ('userId') VALUES (?)", (user_id,))
        return self.conn.commit()

    def addLocationData(self, user_id, latitude, longitude, region, timeShift):
        """Добавляем данные о геопозии юзера"""
        self.cursor.execute("INSERT INTO 'location' ('userId', 'latitude', 'longitude', 'region', 'timeShift') VALUES (?,?,?,?,?)",
            (user_id,
            latitude,
            longitude,
            region,
            timeShift))
            
        return self.conn.commit()


    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()

