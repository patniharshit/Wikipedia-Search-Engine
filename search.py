offset_dict = {}


def read_offsets(field):
    ifile = open("./index/" + field + "_offset", "r")
    print(ifile)
    temp_dict = {}
    for line in ifile:
        tokens = line.split(" ")
        temp_dict[tokens[0]] = int(tokens[1][:-1])
    return temp_dict


def parse_query:
    pass


def main():
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
                query = toks[1]
                query = parse_query(list(query))
                offs = offset_dict[key][query]
            else:
                toks = query.split(' ')
                toks = parse_query(toks)

if __name__ == '__main__':
    main()