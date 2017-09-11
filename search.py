import math
from stopWords import StopWords
from Stemmer import Stemmer

offset_dict = {}
stop_words = StopWords()
stop_words.readStopWords()
stemmer = Stemmer('english')

field_map = {'b': 'body', 't': 'title', 'c': 'categ', 'e': 'links'}

def read_num_docs():
    ifile = open("./index/cntfile", "r")
    temp = 0
    for line in ifile:
        temp = int(line)
    return temp


def tfidf(term_freq, num_doc):
    return (1+math.log10(term_freq)) * math.log10(num_doc)


def read_offsets(field):
    ifile = open("./index/" + field + "_offset", "r")
    temp_dict = {}
    for line in ifile:
        tokens = line.split(" ")
        temp_dict[tokens[0]] = int(tokens[1][:-1])
    return temp_dict


def parse_query(query):
    temp = []
    for w in query:
        w = stemmer.stemWord(w.lower())
        if not stop_words.isStopWord(w):
            temp.append(w)
    return temp


def main():
    num_doc = read_num_docs()
    offset_dict['b'] = read_offsets("body")
    offset_dict['t'] = read_offsets("title")
    offset_dict['c'] = read_offsets("categ")
    offset_dict['e'] = read_offsets("links")

    exit = False
    while not exit:
        query = str(raw_input("Enter query: "))
        if(query == 'q'):
            exit = True
        else:
            if(':' in query):
                toks = query.split(':')
                key = toks[0]
                query = toks[1].split(' ')
                query = parse_query(query)
                docs = {}
                for curr_query in query:
                    offs = offset_dict[key][curr_query]
                    tempfile = open("./index/" + field_map[key] + ".index", "r")
                    tempfile.seek(offs)
                    temp_line = tempfile.readline()
                    tempfile.close()

                    temp_toks = (temp_line.split(' '))[1:]
                    temp_idf = (len(temp_toks))/2
                    temp_tf = 0
                    for entry in query:
                        if(entry == curr_query):
                            temp_tf = temp_tf + 1
                    wtq = tfidf(temp_tf, temp_idf)

                    for i in range(0, len(temp_toks), 2):
                        if temp_toks[i] not in docs:
                            docs[temp_toks[i]] = float(temp_toks[i+1])*wtq
                        else:
                            docs[temp_toks[i]] += float(temp_toks[i+1])*wtq

                    temp_tf = 0

                output_docs = []
                for w in sorted(docs, key=docs.get, reverse=True):
                    output_docs.append(w)
                output_docs = output_docs[:10]
                print(output_docs)
            else:
                toks = query.split(' ')
                toks = parse_query(toks)

if __name__ == '__main__':
    main()