import datetime as dt

class TimezoneModel:
    def __init__(self, hours=None, minutes=None, location=None):
        self.hours = hours
        self.minutes = minutes
        self.location = location
        self.validationMessage = ""

    def validateModel(self):
        if (False):
            self.validationMessage += "Год должен быть текущим, либо в будующем"