import datetime as dt

class Notification:
    def __init__(self, year=None, month=None, day=None, hours=None, minutes=None):
        userId = None
        chatId = None
        self.year = year
        self.month = month
        self.day = day
        self.hours = hours
        self.minutes = minutes
        self.validationMessage = ""

    def validateModel(self):
        if (self.year < dt.datetime.today().year):
            self.validationMessage += "Год должен быть текущим, либо в будующем"

    def validateDate(self):
        result = False
        now = dt.datetime.today()

        if not(self.year):
            self.year = now.year
        if not(self.month):
            self.month = now.month
        if not(self.day):
            self.day = now.day

        try:
            result = dt.datetime(int(self.year), int(self.month), int(self.day))
        except ValueError:
            return False

        if (result.date() < now.date()):
            return False
        else:
            return result