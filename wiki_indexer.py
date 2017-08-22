import xml.etree.ElementTree as etree
import os
import sys
import re
from stopWords import StopWords
from Stemmer import Stemmer

reload(sys)
sys.setdefaultencoding('utf8')

argv = sys.argv

PATH_WIKI_XML = './'
FILENAME_WIKI = './wiki-search-small.xml'
ENCODING = "utf-8"

stop_words = StopWords()
stop_words.readStopWords()
stemmer = Stemmer('english')
freq = {}
doc_freq = {}

category_detection = re.compile(u"\[\[Category:(.*?)\]\]", re.M)


def getCategories(text):
    cate = []
    matches = re.finditer(category_detection, text)
    if matches:
        for match in matches:
            temp = match.group(1).split("|")
            if temp:
                cate.extend(temp)
    data = ' '.join(cate)
    tokenisedWords = re.findall("\d+|[\w]+", data)
    tokenisedWords = [key.encode('utf-8') for key in tokenisedWords]
    return tokenisedWords

def getExternalLinks(text):
    links = []
    data = text
    lines = data.split("==External links==")
    if len(lines) > 1:
        lines = lines[1].split("\n")
        for i in xrange(len(lines)):
            if '* [' in lines[i] or '*[' in lines[i]:
                word = ""
                temp = lines[i].split(' ')
                temp = temp[2:]
                word = [key for key in temp if 'http' not in temp]
                word = ' '.join(word).encode('utf-8')
                links.append(word)
    data = ' '.join(links)
    tokenisedWords = re.findall("\d+|[\w]+", data)
    tokenisedWords = [key.encode('utf-8') for key in tokenisedWords]
    return tokenisedWords


def write_to_disk():
    file = open(argv[2], "w")
    # ans = sorted(freq, key=lambda key: freq[key])
    for key in sorted(freq.keys()):
        file.write(str(key)+":"+str(freq[key])+'\n')


def update_dict(docid):
    for key in doc_freq:
        if key == '':
            continue
        b = doc_freq[key][0]
        t = doc_freq[key][1]
        e = doc_freq[key][2]
        c = doc_freq[key][3]
        strg = 'd'+str(id)
        if b > 0:
            strg = strg + 'b' + str(b)
        if t > 0:
            strg = strg + 't' + str(t)
        if e > 0:
            strg = strg + 'e' + str(e)
        if c > 0:
            strg = strg + 'c' + str(c)
        if key not in freq:
            freq[key] = strg
        else:
            freq[key] = freq[key] + '|' + strg


def process_body_text(text):
    tokens = re.split(r"[^A-Za-z]+", text)
    temp = []
    for w in tokens:
        w = stemmer.stemWord(w.lower())
        if not stop_words.isStopWord(w):
            temp.append(w)
    return temp


def process_lists(text):
    temp = []
    tokens = re.split(r"[^A-Za-z]+", text)
    for w in tokens:
        w = stemmer.stemWord(w.lower())
        if not stop_words.isStopWord(w):
            temp.append(w)
    return temp


def process_lists_categories(text):
    temp = []
    for w in text:
        w = stemmer.stemWord(w.lower())
        if not stop_words.isStopWord(w):
            temp.append(w)
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

for event, elem in etree.iterparse(argv[1], events=('start', 'end')):
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
            title = str(elem.text)
            title_terms = process_lists(title)
            for w in title_terms:
                if w not in doc_freq:
                    doc_freq[w] = (0, 1, 0, 0)
                else:
                    hold = doc_freq[w]
                    doc_freq[w] = (hold[0], hold[1]+1, hold[2], hold[3])
        elif tname == 'id' and not inrevision:
            id = int(elem.text)
        elif tname == 'page':
            totalCount += 1
            print(totalCount)
            if totalCount > 100:
                break
        elif tname == 'text':
            if elem.text is not None:
                templinks = getExternalLinks(elem.text)
                external_links = templinks

                categories = getCategories(str(elem.text))

                body_terms = process_body_text(str(elem.text))
                for w in body_terms:
                    if w not in doc_freq:
                        doc_freq[w] = (1, 0, 0, 0)
                    else:
                        hold = doc_freq[w]
                        doc_freq[w] = (hold[0]+1, hold[1], hold[2], hold[3])

                link_terms = process_lists_categories(external_links)
                for w in link_terms:
                    if w not in doc_freq:
                        doc_freq[w] = (0, 0, 1, 0)
                    else:
                        hold = doc_freq[w]
                        doc_freq[w] = (hold[0], hold[1], hold[2]+1, hold[3])

                cat_terms = process_lists_categories(categories)
                for w in cat_terms:
                    if w not in doc_freq:
                        doc_freq[w] = (0, 0, 0, 1)
                    else:
                        hold = doc_freq[w]
                        doc_freq[w] = (hold[0], hold[1], hold[2], hold[3]+1)
                update_dict(id)
        elem.clear()

# ans = sorted(freq, key=lambda key: freq[key], reverse=True)
write_to_disk()
print("Total pages: {:,}".format(totalCount))
