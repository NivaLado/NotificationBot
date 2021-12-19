import re
import spacy
from spacy.lang.ru.examples import sentences
import enchant 
import pymorphy2
import datetime as dt

# Init
nlp = spacy.load("ru_core_news_md") # Used to get tokens from string
morph = pymorphy2.MorphAnalyzer()   # Used to convert to normal form
dictionary = enchant.Dict("ru_RU")  # Used to correct typos in words
timePattern = "^(-|\+)?([0-1]?[0-9]|2[0-3])[:][0-5]?[0-9]$"
timePatternWithoutDelimeter = "^(-|\+)?([0-1]?[0-9]|2[0-3])$"
datePattern = "^(\d{1,2}\/)(\d{1,2})(\/\d{4})?$"
timePharazesList = ["завтра"]

class SpacyNLP:
    def getDateAndTimeFromString(self, string):
        string = nlp(string)

        for token in string:
            # Recognize time patterns
            if re.match(timePattern,token.text):
                self.getHoursAndMunutesFromString(re.search(timePattern,token.text).group(0))
            elif re.match(timePatternWithoutDelimeter,token.text): 
                self.getHoursFromString(re.search(timePatternWithoutDelimeter,token.text).group(0))
            # Recokognize date patterns
            elif re.match(datePattern,token.text): 
                self.getDateFromString(re.search(datePattern,token.text).group(0))

            #print(token.text, token.pos_, token.dep_)


        return True

    def getHoursFromString(self, timeString):
        return print(int(timeString))

    def getHoursAndMunutesFromString(self, timeString):
        if "-" in timeString or "+" in timeString:
            print("Hours " + timeString[0:3])
            print("Minutes " + timeString[4:6])
        else:
            print("Hours " + timeString[0:2])
            print("Minutes " + timeString[3:5])

    def getDateFromString(self, dateString):
        string = str(dateString)
        count = string.count("/")
        splittedString = string.split("/")

        print("Date: " + splittedString[0])
        print("Month: " + splittedString[1])

        if count == 2:
            print("Year: " + splittedString[2])

#spacyService = SpacyNLP()
#result = spacyService.getDateAndTimeFromString("1/1/2021")
#print(result)

#Завтра к +23:00 поставить будильник в школу

# class Notification:
#     def __init__(self, year, month, day, hour, minutes):
#         self.year = year
#         self.month = month
#         self.day = day
#         self.hour = hour
#         self.minute = minutes
#         self.validationMessage = ""

#     def validateModel(self):
#         if (self.year < dt.datetime.today().year):
#             self.validationMessage += "Год должен быть текущим, либо в будующем"

# ntf = Notification(2020,1,1,1,1)
# ntf.validateModel()
# print(ntf.validationMessage)