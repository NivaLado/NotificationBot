import re

from models.timezoneModel import TimezoneModel
from models.notificationModel import Notification

# Init
timezonePattern = "^(-|\+)?([0-1]?[0-9]|2[0-3])[:][0-5]?[0-9]$"
timezonePatternWithoutDelimeter = "^(-|\+)?([0-1]?[0-9]|2[0-3])$"

timePattern = "^(\+)?([0-1]?[0-9]|2[0-3])[:][0-5]?[0-9]$"
timePatternWithoutDelimeter = "^(\+)?([0-1]?[0-9]|2[0-3])$"

datePattern = "^(?:\d{1,2}(\/)?)(\/\d{1,2}(\/)?)?(\/\d{4})?$"

class DateTimeParser:
    def matchTimezoneFromString(self, timezoneString):
        string = timezoneString.split()
        for token in string:
            if re.match(timezonePattern,token):
                return self.getHoursAndMunutesFromString(re.search(timezonePattern,token).group(0))
            elif re.match(timezonePatternWithoutDelimeter,token): 
                return self.getHoursFromString(re.search(timezonePatternWithoutDelimeter,token).group(0))
                
        return False

    def matchTimeFromString(self, timeString):
        string = timeString.split()
        for token in string:
            if re.match(timePattern,token):
                return self.getHoursAndMunutesFromString(re.search(timePattern,token).group(0))
            elif re.match(timePatternWithoutDelimeter,token): 
                return self.getHoursFromString(re.search(timePatternWithoutDelimeter,token).group(0))
                    
            return False

    def matchDateFromString(self, dateString):
        string = dateString.split()
        for token in string:
            if re.match(datePattern,token): 
                return self.getDateFromString(re.search(datePattern,token).group(0))
                
        return False

    def getHoursFromString(self, timeString):
        timeZoneModel = TimezoneModel()
        timeZoneModel.hours = int(timeString)
        return timeZoneModel

    def getHoursAndMunutesFromString(self, timeString):
        timeZoneModel = TimezoneModel()
        hours, minutes = map(int, timeString.split(':'))
        timeZoneModel.hours = hours
        timeZoneModel.minutes = minutes

        return timeZoneModel

    def getDateFromString(self, dateString):
        dateModel = Notification()
        string = str(dateString)
        count = string.count("/")
        splittedString = string.split("/")

        dateModel.day = int(splittedString[0])

        if count >= 1:
            dateModel.month = int(splittedString[1])
        if count >= 2:
            dateModel.year = int(splittedString[2])

        return dateModel