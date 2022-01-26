import re
import spacy

from models.timezoneModel import TimezoneModel
from models.notificationModel import Notification

# Init
nlp = spacy.load("ru_core_news_md") # Used to get tokens from string
timezonePattern = "^(-|\+)?([0-1]?[0-9]|2[0-3])[:][0-5]?[0-9]$"
timezonePatternWithoutDelimeter = "^(-|\+)?([0-1]?[0-9]|2[0-3])$"

timePattern = "^(\+)?([0-1]?[0-9]|2[0-3])[:][0-5]?[0-9]$"
timePatternWithoutDelimeter = "^(\+)?([0-1]?[0-9]|2[0-3])$"

datePattern = "^(?:\d{1,2}(\/)?)(\/\d{1,2}(\/)?)?(\/\d{4})?$"

class DateTimeParser:
    def matchTimezoneFromString(self, timezoneString):
        string = nlp(timezoneString)
        for token in string:
            if re.match(timezonePattern,token.text):
                return self.getHoursAndMunutesFromString(re.search(timezonePattern,token.text).group(0))
            elif re.match(timezonePatternWithoutDelimeter,token.text): 
                return self.getHoursFromString(re.search(timezonePatternWithoutDelimeter,token.text).group(0))
                
        return False

    def matchTimeFromString(self, timeString):
        string = nlp(timeString)
        for token in string:
            if re.match(timePattern,token.text):
                return self.getHoursAndMunutesFromString(re.search(timePattern,token.text).group(0))
            elif re.match(timePatternWithoutDelimeter,token.text): 
                return self.getHoursFromString(re.search(timePatternWithoutDelimeter,token.text).group(0))
                    
            return False

    def matchDateFromString(self, dateString):
        string = nlp(dateString)
        for token in string:
            if re.match(datePattern,token.text): 
                return self.getDateFromString(re.search(datePattern,token.text).group(0))
                
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

        dateModel.day = splittedString[0]

        if count >= 1:
            dateModel.month = splittedString[1]
        if count >= 2:
            dateModel.year = splittedString[2]

        return dateModel