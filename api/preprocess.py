# import nltk
import re

# nltk.download('stopwords')
from nltk.corpus import stopwords as eng_stopwords

from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from bnunicodenormalizer import Normalizer

import stopwordsiso as stopwords

# initialize
bnorm = Normalizer()

class Document_linearization:
    def pre_process(self, input_text):
        """
        Description: Performs text normalisation, removes punctuations and stop words and returns a list of tokens
        :param input_text:  The text which needs to be cleaned.
        :return: list of tokens
        """
        stop_words = stopwords.stopwords("bn").union(set(eng_stopwords.words('english')),
                                                     {'একটা', 'তাঁহার', 'দিয়া', 'বলিয়া', 'লইয়া', 'আসিয়া', 'লাগিল',
                                                      'কহিল', 'আসিয়া', 'তাহাকে', 'করিল', 'কহিলেন', 'কোনটি', 'ধরনের',
                                                      'বলিলেন', 'করিত', 'চলিয়া', 'ধরিয়া', 'পড়িয়া', 'করিবার', 'হইত',
                                                      'নহে', 'ফিরিয়া', 'কেহ', 'বলিতে', 'রহিল', 'পড়িল', 'উঠিল',
                                                      'বাহির', 'দেখিয়া', 'উঠিয়া', 'ফিরিয়া', 'অবশেষে', 'কিছুতেই',
                                                      'তেমনি', 'তোমাকে', 'নে', 'মাঝে', 'সকল', 'অত্যন্ত', 'একটু',
                                                      'একেবারে', 'এক', 'একটা', 'একদিন', 'কথা', 'তারই', 'হয়ে', 'হওয়ায়',
                                                      'রয়েছে', 'এমনকি', 'একজন', 'দিয়েছেন', 'একটা', 'হয়নি', 'সাথে',
                                                      'হয়েই', 'দিয়ে', 'কেমনে', 'করিয়ে', 'তোরা', 'জন্যে', 'পেয়ে',
                                                      'পাওয়া', 'তোর', 'ছাড়া', 'ছাড়াও', 'হওয়ার', 'তোমাদের', 'চেয়ে',
                                                      'কথা', 'জানিয়েছে', 'মত', 'অর্থাৎ', 'গিয়েছে', 'জাানিয়ে', 'হয়েছে',
                                                      'হিসেবে', 'হওয়া', 'এলো', 'করায়', 'তাঁহারা', 'দেওয়ার', 'হইয়া',
                                                      'হয়েছেন', 'তোদের', 'অর্ধভাগে', 'তিনই', 'এসো', 'দেয়', 'এক', 'যায়',
                                                      'দিয়েছে', 'চায়', 'হয়েছিল', 'তুই', 'হয়তো', 'হৈতে', 'অনুযায়ী',
                                                      'কয়েকটি', 'পাঁচ', 'করিয়া', 'সময়', 'থাকায়'})

        # Perform text normalisation
        # Reference: https://nbviewer.jupyter.org/url/anoopkunchukuttan.github.io/indic_nlp_library/doc/indic_nlp_examples.ipynb#Text-Normalization
        factory = IndicNormalizerFactory()
        normalizer = factory.get_normalizer("bn", remove_nuktas=False)
        output_text = normalizer.normalize(input_text)
        # output_text = bnorm(output_text)
        if output_text == None:
            return []

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
        filtered_sentence = []
        for w in terms:
            if w not in stop_words:
                filtered_sentence.append(w)
        terms = filtered_sentence
        return terms