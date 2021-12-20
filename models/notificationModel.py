import datetime as dt

class Notification:
    def __init__(self, year=None, month=None, day=None, hours=None, minutes=None):
        self.year = year
        self.month = month
        self.day = day
        self.hours = hours
        self.minutes = minutes
        self.validationMessage = ""

    def validateModel(self):
        if (self.year < dt.datetime.today().year):
            self.validationMessage += "Год должен быть текущим, либо в будующем"