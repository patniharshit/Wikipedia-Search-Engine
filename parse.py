import xml.etree.ElementTree as etree
import os
import sys
import re
import ipdb;
from stopWords import StopWords
from Stemmer import Stemmer

reload(sys)
sys.setdefaultencoding('utf8')

PATH_WIKI_XML = './'
FILENAME_WIKI = './wiki-search-small.xml'
ENCODING = "utf-8"

stop_words = StopWords()
stop_words.readStopWords()
stemmer = Stemmer('english')
freq = {}
doc_freq = {}


def write_to_disk():
    file = open("testfile.txt", "w")
    ans = sorted(freq, key=lambda key: freq[key])
    for key in ans:
        file.write(str(key)+":"+str(freq[key])+'\n')


def update_dict(cat):
    if cat == 't':
        pass
    elif cat == 'b':
        for key in doc_freq:
            if key not in freq:
                freq[key] = 'd'+str(id)+'t0b1'
            else:
                freq[key] = freq[key] + str('|d'+str(id)+'t0b'+str(doc_freq[key][1]+1))


def process_text(text):
    # ipdb.set_trace()
    tokens = re.split(r"[^A-Za-z]+", text)
    temp = []
    for w in tokens:
        if not stop_words.isStopWord(w.lower()):
            temp.append(stemmer.stemWord(w.lower()))
    return temp


def strip_tag_name(t):
    t = elem.tag
    idx = t.rfind("}")
    if idx != -1:
        t = t[idx + 1:]
    return t


pathWikiXML = os.path.join(PATH_WIKI_XML, FILENAME_WIKI)

totalCount = 0
articleCount = 0
title = None

for event, elem in etree.iterparse(pathWikiXML, events=('start', 'end')):
    tname = strip_tag_name(elem.tag)

    if event == 'start':
        if tname == 'page':
            title = ''
            id = -1
            redirect = ''
            inrevision = False
            ns = 0
            doc_freq.clear()
        elif tname == 'revision':
            inrevision = True
    else:
        if tname == 'title':
            title = elem.text
            # title_terms = process_text(elem.text)
            # update_dict(id, title_terms, 't')
        elif tname == 'id' and not inrevision:
            id = int(elem.text)
        elif tname == 'page':
            totalCount += 1
            print(totalCount)
            if totalCount > 100000000:
                break
        elif tname == 'text':
            if elem.text is not None:
                body_terms = process_text(elem.text)
                for w in body_terms:
                    if w not in doc_freq:
                        doc_freq[w] = (0, 1)
                    else:
                        doc_freq[w] = (doc_freq[w][0], doc_freq[w][1])
                update_dict('b')
        elem.clear()

# ans = sorted(freq, key=lambda key: freq[key], reverse=True)
write_to_disk()
print("Total pages: {:,}".format(totalCount))
