import datetime as dt

class TimezoneModel:
    def __init__(self, hours=None, minutes=0, location=None):
        self.hours = hours
        self.minutes = minutes
        self.location = location
        self.latitude = None
        self.longitude = None
        self.validationMessage = ""

    def validateModel(self):
            self.validationMessage += "Год должен быть текущим, либо в будующем"