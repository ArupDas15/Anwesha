from helper import read_csv_dict,read_unigram_probs,create_reverse_dic
from indictrans import Transliterator
import Spellchecker


word_set = read_csv_dict('Bangla_dictionary.csv')
word_set = word_set.union(read_csv_dict('More_bangla_words.csv'))
unigrams = read_unigram_probs('count_eng.txt') 
reverse_dict = create_reverse_dic('Bangla_dictionary.csv','More_bangla_words.csv')
trn = Transliterator(source='ben', target='eng', build_lookup=True)
checker_DM = Spellchecker.SpellChecker_DM(word_set, unigrams, 1, lamda=0.05)
word = 'বাংল'
guesses = checker_DM.correct(trn.transform(word),1)
true_guesses = []
for guess in guesses:
  true_guesses.append((reverse_dict[guess[0]],guess[1]))
print(guesses)
print(true_guesses)