from operator import le
from pydoc import Helper
from flask import Flask,request
from flask import request
from flask_cors import CORS
import load
import sys,os

from Bangla_Spellchecker.helper import read_csv_dict, read_unigram_probs, create_reverse_dic
from indictrans import Transliterator
from Bangla_Spellchecker.Spellchecker import SpellChecker_DM
import os



search_path = os.path.join(os.getcwd())
sys.path.append(os.path.join(search_path, 'Bangla_Spellchecker'))
word_set = read_csv_dict(os.path.join(search_path, 'Bangla_Spellchecker', 'Bangla_dictionary.csv'))
word_set = word_set.union(read_csv_dict(os.path.join(search_path, 'Bangla_Spellchecker', 'More_bangla_words.csv')))
unigrams = read_unigram_probs(os.path.join(search_path, 'Bangla_Spellchecker', 'count_eng.txt'))
reverse_dict = create_reverse_dic(os.path.join(search_path, 'Bangla_Spellchecker', 'Bangla_dictionary.csv'),
                                  os.path.join(search_path, 'Bangla_Spellchecker', 'More_bangla_words.csv'))
trn = Transliterator(source='ben', target='eng', build_lookup=True)
checker_DM = SpellChecker_DM(word_set, unigrams, 1, lamda=0.05)

sys.path.append(os.path.join(search_path, 'Bangla_Spellchecker', 'Lemmatization'))

app = Flask(__name__)
CORS(app)


# If you wish to save the lemmatisation model then give the dataset path as: os.path.join('Lemmatization', 'Lemmatization')
searchEngineObject = load.SearchEngine()


@app.route('/')
def home_page():
    print("welcome to the bangla search engine",request.host)




@app.route('/search')
def get_search_results():
    search_query = request.args.get('q')
    search_query_terms = search_query.split(" ")
    correction_detected = False
    spellcheck = {}
    for term in search_query_terms:
        word = trn.transform(term)
        spellcheck[term] = []
        spellcheck[term].append(term)
        if word not in reverse_dict.keys():
            correction_detected = True
            guesses = checker_DM.correct(word, 5)
            for guess in guesses:
                # todo add the candidate solution only for some threshold value
                spellcheck[term].append(reverse_dict[guess[0]])

    model = request.args.get('m')
    lemmatiser = request.args.get('lemmatiser')

    if lemmatiser == 'true':
        lem_flag = True
    elif lemmatiser == 'false':
        lem_flag = False

    print("THE QUERY IS " + search_query + " AND THE MODEL IS " + model)
    if model == 'model_0':
        res = searchEngineObject.model_tfidf(search_query, lemmatiser=lem_flag)
    elif model == "model_1":
        res = searchEngineObject.model_tfidf_qe(search_query, lemmatiser=lem_flag)
    elif model == "model_2":
        res = searchEngineObject.model_lsa(search_query, lemmatiser=lem_flag)
    elif model == "model_3":
        res = searchEngineObject.model_lsa_qe(search_query, lemmatiser=lem_flag)
    elif model == "model_4":
        res = searchEngineObject.model_esa(search_query, lemmatiser=lem_flag)
    elif model == "model_5":
        res = searchEngineObject.model_esa_qe(search_query, lemmatiser=lem_flag)

    spellcheck["correction_detected"] = correction_detected
    spellcheck["query_terms"] = search_query_terms

    res["spellcheck"] = spellcheck

    return res