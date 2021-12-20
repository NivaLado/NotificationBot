import sqlite3

class Repository:

    def __init__(self, dbFile):
        """Инициализация соединения с БД"""
        self.conn = sqlite3.connect(dbFile)
        self.cursor = self.conn.cursor()

    def userExists(self, userId):
        """Проверяем, есть ли юзер в БД"""
        result = self.cursor.execute("SELECT 'id' FROM 'users' WHERE 'userId' = ?", (userId,))
        return bool(len(result.fetchall()))

    def getUserId(self, userId):
        """Получаем ID юзера в из БД по его userId в Телеграмме"""
        result = self.cursor.execute("SELECT 'id' FROM 'users' WHERE 'userId' = ?", (userId,))
        return result.fetchone()[0]

    def addUser(self, userId, chatId, userName):
        """Добавляем юзера в БД"""
        self.cursor.execute("INSERT INTO 'users' ('userId', 'chatId', 'userName') VALUES (?,?,?)", (userId, chatId, userName))
        return self.conn.commit()

    def addLocationData(self, userId, latitude, longitude, region, hoursShift, minutesShift):
        """Добавляем данные о геопозии юзера"""
        self.cursor.execute("INSERT INTO 'location' ('userId', 'latitude', 'longitude', 'region', 'hoursShift', 'minutesShift') VALUES (?,?,?,?,?, ?)",
            (userId,
            latitude,
            longitude,
            region,
            hoursShift,
            minutesShift))
            
        return self.conn.commit()

    def updateLocationData(self, userId, latitude, longitude, region, hoursShift, minutesShift):
        """Обновляем данные о геопозии юзера"""
        self.cursor.execute("UPDATE 'location' SET latitude = ?, longitude = ?, region = ?, hoursShift = ?, minutesShift = ? WHERE userId = ?",
            (latitude,
            longitude,
            region,
            hoursShift,
            minutesShift,
            userId))
        
        return self.conn.commit()

    def locationDataExists(self, userId):
        """Проверка на наличие наличия таймзоны"""
        result = self.cursor.execute("SELECT id FROM 'location' WHERE userId = ?", (userId,))
        row = result.fetchone()
        if row == None:
            return False
        else:
            return True

    def addOrUpdateLocationData(self, userId, latitude, longitude, region, hoursShift, minutesShift):
        """Create record if it doese't exist or update existing"""
        if (self.locationDataExists(userId)):
            self.updateLocationData(userId, latitude, longitude, region, hoursShift, minutesShift)
        else:
            self.addLocationData(userId, latitude, longitude, region, hoursShift, minutesShift)

    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()

