import spacy
from spacy.lang.ru.examples import sentences
import enchant 
import pymorphy2

# init
#morph = pymorphy2.MorphAnalyzer()
#x = morph.parse('машины')[0]
#print(x.normal_form)

thisdict = {
  "завтра": 1,
  "вчера": -1,
  "неделю": 1964
}


#dictionary = enchant.Dict("ru_RU")
#print(dictionary.check("Приaффвет"))
#print(dictionary.suggest("Приaвет"))

nlp = spacy.load("ru_core_news_md")
doc = nlp("8 восемь")

print(doc.text)
for token in doc:
    print(token.text, token.pos_, token.dep_)