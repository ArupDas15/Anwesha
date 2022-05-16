import csv


def read_csv_dict(dictfile):
    with open(dictfile, encoding='utf8') as fp:
        csv_reader = csv.reader(fp)
        dict_words = set([word.replace("\"", "").strip().lower() for _, word, in csv_reader])
    return dict_words


"""
	Read word list file 
"""


def read_list_dict(dictfile):
    with open(dictfile) as fp:
        words = set([line.strip() for line in fp])
    return words


"""
	Reads unigrams and corresponding frequency counts
"""


def read_unigram_probs(unigram_file):
    with open(unigram_file, encoding='utf8') as fp:
        lines = [[tok.strip() if i == 0 else int(tok.strip()) for i, tok in enumerate(line.split(' '))] for line in fp]
    return lines


def create_reverse_dic(main_dictfile, add_dictfile=" "):
    reverse_dict = {}
    with open(main_dictfile, encoding='utf8') as fp:
        csv_reader1 = csv.reader(fp)
        for ben_word, eng_word in csv_reader1:
            if eng_word not in reverse_dict:
                reverse_dict[eng_word] = ben_word

    if add_dictfile != " ":
        with open(add_dictfile, encoding='utf8') as fp:
            csv_reader2 = csv.reader(fp)

            for ben_word, eng_word in csv_reader2:
                if eng_word not in reverse_dict:
                    reverse_dict[eng_word] = ben_word

    return reverse_dict


