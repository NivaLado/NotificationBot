import sqlite3

from models.timezoneModel import TimezoneModel
from models.notificationModel import Notification

class Repository:

    def __init__(self, dbFile):
        self.conn = sqlite3.connect(dbFile)
        self.cursor = self.conn.cursor()

    def userExists(self, userId):
        result = self.cursor.execute("SELECT 'id' FROM 'users' WHERE 'userId' = ?", (userId,))
        return bool(len(result.fetchall()))

    def getUserId(self, userId):
        result = self.cursor.execute("SELECT 'id' FROM 'users' WHERE 'userId' = ?", (userId,))
        return result.fetchone()[0]

    def addUser(self, userId, chatId, userName):
        self.cursor.execute("INSERT INTO 'users' ('userId', 'chatId', 'userName') VALUES (?,?,?)", (userId, chatId, userName))
        return self.conn.commit()

    def addLocationData(self, userId, latitude, longitude, region, hoursShift, minutesShift):
        self.cursor.execute("INSERT INTO 'location' ('userId', 'latitude', 'longitude', 'region', 'hoursShift', 'minutesShift') VALUES (?,?,?,?,?, ?)",
            (userId,
            latitude,
            longitude,
            region,
            hoursShift,
            minutesShift))
            
        return self.conn.commit()

    def updateLocationData(self, userId, latitude, longitude, region, hoursShift, minutesShift):
        self.cursor.execute("UPDATE 'location' SET latitude = ?, longitude = ?, region = ?, hoursShift = ?, minutesShift = ? WHERE userId = ?",
            (latitude,
            longitude,
            region,
            hoursShift,
            minutesShift,
            userId))
        
        return self.conn.commit()

    def locationDataExists(self, userId):
        result = self.cursor.execute("SELECT id FROM 'location' WHERE userId = ?", (userId,))
        row = result.fetchone()
        if row == None:
            return False
        else:
            return True

    def addOrUpdateLocationData(self, userId, latitude, longitude, region, hoursShift, minutesShift):
        if (self.locationDataExists(userId)):
            self.updateLocationData(userId, latitude, longitude, region, hoursShift, minutesShift)
        else:
            self.addLocationData(userId, latitude, longitude, region, hoursShift, minutesShift)

    def tryToGetLocationData(self, userId):
        result = self.cursor.execute("SELECT hoursShift, minutesShift, region  FROM 'location' WHERE userId = ?", (userId,))
        row = result.fetchone()
        if row == None:
            return False
        else:
            return TimezoneModel(row[0], row[1], row[2])

    def addNotification(self, userId, chatId, message, notificationDateTime):
        self.cursor.execute("INSERT INTO 'notifications' ('userId', 'chatId', 'message', 'notificationDateTime') VALUES (?,?,?,?)", (userId, chatId, message, notificationDateTime))
        return self.conn.commit()

    def getAllNotificationsByUserId(self, userId):
        result = self.cursor.execute("""
            SELECT
                nt.message,
                nt.chatId,
                nt.notificationDateTime
            FROM
                'notifications' nt
            INNER JOIN 
                'location' loc 
                ON loc.userId = nt.userId
            WHERE nt.userId = ?""", (userId,))

        rows = result.fetchall()
        if rows == None:
            return False
        else:
            notificationList = []
            for notification in rows:
                notificationModel = Notification()
                notificationModel.message = notification[0]
                notificationModel.chatId = notification[1]
                notificationModel.notificationDateTime = notification[2]
                notificationList.append(notificationModel)

            return notificationList
            


    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()

