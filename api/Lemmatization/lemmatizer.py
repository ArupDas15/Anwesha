import warnings
import os
import stopwordsiso as stopwords
import re
import pyiwn
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords as eng_stopwords
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from bnunicodenormalizer import Normalizer
from bnlp import NLTKTokenizer
from bnlp import POS
from weighted_levenshtein import lev
from indictrans import Transliterator

warnings.filterwarnings("ignore")
# redundant trn is used in server.py
trn = Transliterator(source='ben', target='eng', build_lookup=True)
# Create a IndoWordNet class instance and set a language to access its Wordnet
iwn = pyiwn.IndoWordNet(pyiwn.Language.BENGALI)
bangla_words = iwn.all_words()
# initialize
bnorm = Normalizer()

# Read Noun suffix list.
data_path = os.path.join('Lemmatization', 'suffix.txt')
with open(data_path, 'r', encoding='utf-8') as f:
    test_list = f.read().split('\n')

# Read Root word expansion.
data_path = os.path.join('Lemmatization', 'words.txt')
with open(data_path, 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')


# Punctuation Removal Function
def remove_punc(string):
    punc = '''!()-[]{};|:'"\,<>./?@#$%^&*_~'''
    for ele in string:
        if ele in punc:
            string = string.replace(ele, "")
    return string


# Verbal Look up Table.
data_path = os.path.join('Lemmatization', 'verbal inflections.txt')
with open(data_path, 'r', encoding='utf-8') as f:
    test_list2 = f.read().split('\n')

# Cleaning of verbal inflections
lis = [remove_punc(i) for i in test_list2]

inflected = []
verb = []
n = len(lis)
for i in range(0, n):
    temp = lis[i].split()
    inflected.append(temp[0])
    verb.append(temp[1])

eng = []
for ben in lines:
    temp = [ben, trn.transform(ben)]
    eng.append(temp)
myDict = {}


def fun(bi_grams, word1, beng):  # 3 cases needed to debugged : possibly a dash in between
    try:
        for gram in bi_grams:
            s = ""
            for var in gram:
                s = s + var
            if s in myDict.keys():
                myDict[s].add((word1, beng))
            else:
                myDict[s] = set()
                myDict[s].add((word1, beng))
    except:
        for gram in bi_grams:
            s = ""
            for var in gram:
                s = s + var
            print(s)


for i in range(0, len(eng)):
    words = list(eng[i][1])
    bi_grams = nltk.ngrams(words, 3)
    fun(bi_grams, eng[i][1], eng[i][0])


def getcandidates(word):
    input = word
    input_eng = trn.transform(input)
    words = list(input_eng)
    bi_grams = nltk.ngrams(words, 2)
    candidate_list = []
    for gram in bi_grams:
        s = ""
        for var in gram:
            s = s + var
        if s in myDict.keys():
            candidate_list.extend(myDict[s])
    frequency_list = {}
    for i in range(0, len(candidate_list)):
        w = candidate_list[i][0]
        if w in frequency_list.keys():
            frequency_list[w] = (frequency_list[w][0] + 1, frequency_list[w][1])
        else:
            frequency_list[w] = (1, candidate_list[i][1])
    rootwords = []
    for w, value in frequency_list.items():
        if value[0] >= 2:
            temp = []
            temp.append(w)
            temp.append(value[1])
            rootwords.append(temp)
    return rootwords


# Suffix removal function
def rchop(s, suffix):
    return s[:-len(suffix)]


# Root word expansion.
for ben in bangla_words:
    lines.append(ben)


class document_linearization:
    def pre_process(self, input_text):
        """
        Description: Performs text normalisation, removes punctuations and stop words and returns a space separated lemmatised text.
        :param input_text:  The text which needs to be cleaned.
        :return: list of tokens
        """
        stop_words = stopwords.stopwords("bn").union(set(eng_stopwords.words('english')),
                                                     set(['একটা', 'তাঁহার', 'দিয়া', 'বলিয়া', 'লইয়া', 'আসিয়া',
                                                          'লাগিল', 'কহিল', 'আসিয়া', 'তাহাকে', 'করিল', 'কহিলেন',
                                                          'কোনটি', 'ধরনের', 'বলিলেন', 'করিত', 'চলিয়া', 'ধরিয়া',
                                                          'পড়িয়া', 'করিবার', 'হইত', 'নহে', 'ফিরিয়া', 'কেহ', 'বলিতে',
                                                          'রহিল', 'পড়িল', 'উঠিল', 'বাহির', 'দেখিয়া', 'উঠিয়া',
                                                          'ফিরিয়া', 'অবশেষে', 'কিছুতেই', 'তেমনি', 'তোমাকে', 'নে',
                                                          'মাঝে', 'সকল', 'অত্যন্ত', 'একটু', 'একেবারে', 'এক', 'একটা',
                                                          'একদিন', 'কথা', 'তারই', 'হয়ে', 'হওয়ায়', 'রয়েছে', 'এমনকি',
                                                          'একজন', 'দিয়েছেন', 'একটা', 'হয়নি', 'সাথে', 'হয়েই', 'দিয়ে',
                                                          'কেমনে', 'করিয়ে', 'তোরা', 'জন্যে', 'পেয়ে', 'পাওয়া', 'তোর',
                                                          'ছাড়া', 'ছাড়াও', 'হওয়ার', 'তোমাদের', 'চেয়ে', 'কথা',
                                                          'জানিয়েছে', 'মত', 'অর্থাৎ', 'গিয়েছে', 'জাানিয়ে', 'হয়েছে',
                                                          'হিসেবে', 'হওয়া', 'এলো', 'করায়', 'তাঁহারা', 'দেওয়ার', 'হইয়া',
                                                          'হয়েছেন', 'তোদের', 'অর্ধভাগে', 'তিনই', 'এসো', 'দেয়', 'এক',
                                                          'যায়', 'দিয়েছে', 'চায়', 'হয়েছিল', 'তুই', 'হয়তো', 'হৈতে',
                                                          'অনুযায়ী', 'কয়েকটি', 'পাঁচ', 'করিয়া', 'সময়', 'থাকায়']))

        # Perform text normalisation
        # Reference: https://nbviewer.jupyter.org/url/anoopkunchukuttan.github.io/indic_nlp_library/doc/indic_nlp_examples.ipynb#Text-Normalization
        factory = IndicNormalizerFactory()
        normalizer = factory.get_normalizer("bn", remove_nuktas=False)
        output_text = normalizer.normalize(input_text)
        output_text = bnorm(output_text)

        # Remove punctuation from the text.
        text = output_text.strip()
        text = text.replace("’", "")
        text = text.replace("‘", "")
        text = text.replace('”', "")
        text = text.replace("“", "")

        # Some of the punctuation symbols were obtained from here: https://github.com/paul-pias/Text-Preprocessing-in-Bangla-and-English
        clean_text = re.sub(r"[!\"”#$%&’()*+,-./:;<=>?@\[\]^_`{|}~–—\'।॥]+\ *", ' ', text)
        clean_text = re.sub(r"[-—]+\ *", ' ', clean_text)
        clean_text = re.sub(r"\n", ' ', clean_text)
        clean_text = " ".join(clean_text.split())

        # tokenize the cleaned text
        terms = clean_text.split(' ')
        # Remove stop words
        filtered_sentence = ''
        for w in terms:
            if w not in stop_words:
                filtered_sentence = filtered_sentence + ' ' + self.lem(w)
        return filtered_sentence

    # Lemmatization function : Input : single word Output: Single word
    def lem(self, word):
        words = lines
        i = 0
        query = word
        bn_pos = POS()
        model_path = os.path.join("models", "bn_pos.pkl")
        bnltk = NLTKTokenizer()
        # Stores the list of sentence_tokens.
        sentence_tokens = bnltk.sentence_tokenize(query)

        for sentence_no, q_sent in enumerate(sentence_tokens):
            # Generates a tuple of the form: ('WORD', 'TAG')
            tags = bn_pos.tag(model_path, q_sent)
            # Checking if the word is present in the root words dictionary corpus.
            for w in words:
                if w == word:
                    return word
            if tags[0][1] == 'NP':  # Checking for proper noun.
                for suff in test_list[:]:
                    if word.endswith(suff):
                        word = rchop(word, suff)
            # return word
            if tags[0][1] == 'NC' or tags[0][1] == 'NP' or tags[0][1] == 'NV' or tags[0][1] == 'NST':
                for suff in test_list[:]:
                    for w in words:
                        if w == word:
                            return word
                    if word.endswith(suff):
                        word = rchop(word, suff)
            if tags[0][1] == 'VM' or tags[0][1] == 'VA':
                for k in range(0, len(inflected)):
                    if word == inflected[i]:
                        return verb[i]

        A = getcandidates(word)
        n = len(A)
        dist = []
        string1 = word
        for i in range(0, n):
            string2 = A[i][0]
            d = lev(string1, string2)
            dist.append([A[i][0], d])
        distance = 9999999
        root = []

        for i in range(0, n):
            if dist[i][1] < distance:
                distance = dist[i][1]
                root = dist[i][0]
        length = len(string1)
        if distance > length / 2:
            root = string1
        return root

    # Returns a list of tokens from the text.
    # Reference: https://stackoverflow.com/a/50707673
    def identity_tokenizer(self, text):
        terms = text.split(' ')
        if '' in terms:
            # There is an empty string getting added to the vocabulary, so we are removing it from the list of tokens.
            terms.remove('')
        return terms
