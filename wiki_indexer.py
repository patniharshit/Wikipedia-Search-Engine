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
file_cntr = 0
file_step = 500


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


def write_to_disk(cntr):
    bodyfile = open('./index/body'+str(cntr), "w")
    titlefile = open('./index/title'+str(cntr), "w")
    categfile = open('./index/categ'+str(cntr), "w")
    linksfile = open('./index/links'+str(cntr), "w")
    body_str = ""
    title_str = ""
    categ_str = ""
    links_str = ""
    for key in sorted(freq.keys()):
        for tup in freq[key]:
            if(tup[1] != 0):
                body_str += str(tup[0])+'x'+str(tup[1])+'|'
            if(tup[2] != 0):
                title_str += str(tup[0])+'x'+str(tup[2])+'|'
            if(tup[3] != 0):
                categ_str += str(tup[0])+'x'+str(tup[3])+'|'
            if(tup[4] != 0):
                links_str += str(tup[0])+'x'+str(tup[4])+'|'
        if(body_str):
            bodyfile.write(str(key)+":"+str(body_str)+'\n')
        if(title_str):
            titlefile.write(str(key)+":"+str(title_str)+'\n')
        if(categ_str):
            categfile.write(str(key)+":"+str(categ_str)+'\n')
        if(links_str):
            linksfile.write(str(key)+":"+str(links_str)+'\n')
        body_str = ""
        title_str = ""
        categ_str = ""
        links_str = ""


def update_dict(docid):
    flg = False
    for key in doc_freq:
        if key == '':
            continue
        b = doc_freq[key][0]
        t = doc_freq[key][1]
        e = doc_freq[key][2]
        c = doc_freq[key][3]
        if key not in freq:
            freq[key] = []
            freq[key].append((docid, b, t, e, c))
        else:
            freq[key].append((docid, b, t, e, c))


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
            if totalCount > 600:
                write_to_disk(file_cntr)
                elem.clear()
                freq.clear()
                doc_freq.clear()
                file_cntr = file_cntr + 1
                break
            if totalCount % file_step == 0:
                write_to_disk(file_cntr)
                elem.clear()
                freq.clear()
                doc_freq.clear()
                file_cntr = file_cntr + 1
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

print("Total pages: {:,}".format(totalCount))

cntfile = open('./index/cntfile', "w")
cntfile.write(str(totalCount))