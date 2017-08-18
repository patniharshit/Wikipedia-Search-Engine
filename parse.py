import xml.etree.ElementTree as etree
import os
import sys
import re
import ipdb;
from stopWords import StopWords
from nltk.stem.porter import PorterStemmer

reload(sys)
sys.setdefaultencoding('utf8')

PATH_WIKI_XML = './'
FILENAME_WIKI = './wiki-search-small.xml'
ENCODING = "utf-8"

stop_words = StopWords()
stop_words.readStopWords()
stemmer = PorterStemmer()
freq = {}

def write_to_disk():
    file = open("testfile.txt","w")
    ans = sorted(freq, key=lambda key: freq[key])
    for key in ans:
        file.write(str(key) + ": ")
        for entry in freq[key]:
            print('inhere')
            file.write('d'+str(entry[0])+'t'+str(entry[1])+'b'+str(entry[2])+'|')

def update_dict(id, term_list, cat):
    if cat == 't':
        for term in term_list:
            if term not in freq:
                freq[term] = [(id, 1, 0)]
            else:
                for i in range(len(freq[term])):
                    if freq[term][i][0] == id:
                        val = freq[term][i]
                        freq[term][i] = (id, val[1]+1, val[2])
    elif cat == 'b':
        for term in term_list:
            if term not in freq:
                freq[term] = [(id, 0, 1)]
            else:
                if freq[term][-1][0] < id:
                    freq[term].append((id, 0, 1))
                else:
                    for i in range(len(freq[term])):
                        if freq[term][i][0] == id:
                            val = freq[term][i]
                            freq[term][i] = (id, val[1], val[2]+1)

def process_text(text):
    tokens = re.split(r"[^A-Za-z]+", text)
    temp = []
    for w in tokens:
        if not stop_words.isStopWord(w):
            temp.append(stemmer.stem(w.lower()))
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
        elif tname == 'revision':
            inrevision = True
    else:
        if tname == 'title':
            title = elem.text
            # title_terms = process_text(elem.text)
            #update_dict(id, title_terms, 't')
        elif tname == 'id' and not inrevision:
            id = int(elem.text)
        elif tname == 'redirect':
            redirect = elem.attrib['title']
        elif tname == 'page':
            totalCount += 1
            print(totalCount)
            if totalCount > 1000000:
                break
        elif tname == 'text':
            if elem.text is not None:
                body_terms = process_text(elem.text)
                update_dict(id, body_terms, 'b')
        elem.clear()

# ans = sorted(freq, key=lambda key: freq[key], reverse=True)
write_to_disk()
print("Total pages: {:,}".format(totalCount))
