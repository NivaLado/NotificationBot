import re
import spacy
from spacy.lang.ru.examples import sentences
import enchant 
import pymorphy2

# Init
nlp = spacy.load("ru_core_news_md") # Used to get tokens from string
morph = pymorphy2.MorphAnalyzer()   # Used to convert to normal form
dictionary = enchant.Dict("ru_RU")  # Used to correct typos in words
timePattern = "^(-|\+)?([0-1]?[0-9]|2[0-3])[:|\/|.][0-5]?[0-9]$"
timePatternWithoutDelimeter = "^(-|\+)?([0-1]?[0-9]|2[0-3])$"
getHoursFromStringPattern = "(-|\+)?([0-1]?[0-9]|2[0-3])"

class SpacyNLP:
    def getTimeFromString(self, string):
        string = nlp(string)
        result = ""

        for token in string:
            if re.match(timePattern,token.text):
                result = re.search(timePattern,token.text).group(0)
            elif re.match(timePatternWithoutDelimeter,token.text): 
                result = re.search(timePatternWithoutDelimeter,token.text).group(0)
            else:
                return False

        return getHoursFromString(result)

def getHoursFromString(timeString):
    hours = re.search(getHoursFromStringPattern, timeString).group(0)
    return int(hours)

spacyService = SpacyNLP()
result = spacyService.getTimeFromString("+23:00")
result