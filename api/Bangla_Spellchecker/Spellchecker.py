
import math
import csv
import sys
import re
from tkinter import W
import _pickle as cPickle
import numpy as np


from weighted_levenshtein import dam_lev
from tqdm import tqdm
import fuzzy


class SpellChecker_DM:

    def __init__(self, word_set, unigrams, k, costs=None, lamda=1, alphabet='abcdefghijklmnopqrstuvwxyz'):

        # Initialize alphabet
        self.alphabet = alphabet

        # Store all known words
        self.dict_words = word_set

        # Build and store valid prefixes
        # self.valid_prefixes = set([])
        # for word in self.dict_words:
        # 	for i in range(len(word)+1):
        # 		self.valid_prefixes.add(word[:i])

        # Build the bigram index

        self.bigram_index = {}

        for word in self.dict_words:
            for i in range(len(word)):
                bigram = word[i:i+2]
                if bigram not in self.bigram_index.keys():
                    self.bigram_index[bigram] = [word]
                else:
                    self.bigram_index[bigram].append(word)

        # Weighting likelihood & prior
        self.lamda = lamda

        # Store unigram probabilities - Use Laplace Add-k Smoothing for log probabilities
        self.priors = {}
        self.k = k
        self.N = sum((count for word, count in unigrams)) + k*len(unigrams) + k
        for word, count in unigrams:
            self.priors[word] = math.log(float(count+k) / self.N)

        # Edit Distance Costs
        if costs != None:
            self.insert_costs = costs['ins_costs']
            self.delete_costs = costs['del_costs']
            self.substitute_costs = costs['sub_costs']
            self.transpose_costs = costs['trans_costs']
        else:
            self.insert_costs = np.ones((128,))
            self.delete_costs = np.ones((128,))
            self.transpose_costs = np.ones((128, 128))
            self.substitute_costs = np.ones((128, 128))

        # Build phonetic index - Double Metaphone
        self.dmeta = fuzzy.DMetaphone()
        self.phonetic_buckets = {}

        for word in self.dict_words:
            try:
                phonetic_idx = self.dmeta(word)
            except UnicodeEncodeError:
                continue
            if phonetic_idx[0] not in self.phonetic_buckets:
                self.phonetic_buckets[phonetic_idx[0]] = []
            self.phonetic_buckets[phonetic_idx[0]].append(word)

            if phonetic_idx[1] != None:
                if phonetic_idx[1] not in self.phonetic_buckets:
                    self.phonetic_buckets[phonetic_idx[1]] = []
                self.phonetic_buckets[phonetic_idx[1]].append(word)

    def __edit_neighbors_1(self, word):
        word_len = len(word)
        deletions = [(word[:i]+word[i+1:]) for i in range(word_len)]
        insertions = [word[:i]+letter+word[i:]
                      for i in range(word_len+1) for letter in self.alphabet]
        substitutions = [word[:i]+letter+word[i+1:]
                         for i in range(word_len) for letter in self.alphabet]
        transpositions = [word[:i]+word[i+1]+word[i]+word[i+2:]
                          for i in range(word_len-1)]
        return set(deletions + insertions + substitutions + transpositions)

    def __filter_unknown(self, words):
        return set([word for word in words if word in self.dict_words])

    # def __fastGenerateNeighbors(self, left, right, max_dist=2):
        # # Boundary Conditions
        # if max_dist == 0:
        # 	if left+right in self.valid_prefixes:	return [left+right]
        # 	else:									return []

        # if len(right) == 0:
        # 	results = []
        # 	if left in self.valid_prefixes:
        # 		results.append(left)
        # 	for letter in self.alphabet:
        # 		if left + letter in self.valid_prefixes:
        # 			results.append(left + letter)
        # 	return list(set(results))

        # # Update bounds
        # left = left + right[:1]
        # right = right[1:]

        # # Initialize neighbors
        # neighbor_set = []

        # # Deletions
        # if left[:-1] in self.valid_prefixes:
        # 	neighbor_set += self.__fastGenerateNeighbors(left[:-1], right, max_dist-1)

        # # Insertions
        # for letter in self.alphabet:
        # 	if left[:-1]+letter+left[-1:]  in self.valid_prefixes:
        # 		neighbor_set += self.__fastGenerateNeighbors(left[:-1]+letter+left[-1:], right, max_dist-1)

        # # Substitutions
        # for letter in self.alphabet:
        # 	if left[:-1]+letter in self.valid_prefixes:
        # 		neighbor_set += self.__fastGenerateNeighbors(left[:-1]+letter, right, max_dist - (1 if letter != left[-1] else 0))

        # # Transpositions
        # if len(right) >= 1:
        # 	if left[:-1] + right[0] + left[-1] in self.valid_prefixes:
        # 		neighbor_set += self.__fastGenerateNeighbors(left[:-1]+right[0]+left[-1], right[1:], max_dist-1)

        # return list(set(neighbor_set))

    def __jaccard_coeffecient(self, wrong_word, candidate, intersection):

        try:
            score = (intersection/(len(wrong_word) +
                     len(candidate) - 2 - intersection))
        except:
            return 0
        return score

    def __fastGenerateCandidates(self, wrong_word):

        all_bigram_candidates = {}

        for i in range(len(wrong_word)):
            bigram = wrong_word[i:i+2]
            if bigram in self.bigram_index.keys():
                bigram_candidates = self.bigram_index[bigram]
                for bigram_candidate in bigram_candidates:
                    if bigram_candidate in all_bigram_candidates.keys():
                        all_bigram_candidates[bigram_candidate] += 1
                    else:
                        all_bigram_candidates[bigram_candidate] = 1

        jaccard_scores = [(bigram_candidate, self.__jaccard_coeffecient(wrong_word, bigram_candidate,
                           all_bigram_candidates[bigram_candidate])) for bigram_candidate in all_bigram_candidates.keys()]

        sorted_candidates = sorted(jaccard_scores, key=lambda x: -x[1])[:20]

        candidates = [candidate[0] for candidate in sorted_candidates]

        return candidates

    def __generateCandidates(self, wrong_word):
        """
        # Old Approach - Too Slow (remove candidates_2 for fast+efficient)
        candidates = self.__edit_neighbors_1(wrong_word)		
        candidates_2 = set([next_candidate for candidate in candidates for next_candidate in self.__edit_neighbors_1(candidate)])

        candidates = self.__filter_unknown(candidates)
        candidates_2 = self.__filter_unknown(candidates_2)
        """

        # # Edit Distance based candidates
        # candidates = self.__fastGenerateNeighbors('', wrong_word, 2)
        # candidates = self.__filter_unknown(candidates)

        # BIGRAM AND JACCCARD DISTANCE BASED CANDIDATES
        candidates = self.__fastGenerateCandidates(wrong_word)

        # DMetaphone based candidates
        try:
            metaphone_bkts = self.dmeta(wrong_word)
            candidates_meta = self.phonetic_buckets.get(metaphone_bkts[0], []) + (
                self.phonetic_buckets.get(metaphone_bkts[1], []) if metaphone_bkts[1] != None else [])
            candidates_meta = set(candidates_meta)
        except UnicodeEncodeError:
            return candidates

        return (candidates_meta.union(candidates))
        # return candidates

    def generateCandidates(self, wrong_word):
        return self.__generateCandidates(wrong_word)

    def __score(self, wrong_word, candidate):
        dl_dist = dam_lev(wrong_word, candidate, insert_costs=self.insert_costs, substitute_costs=self.substitute_costs,
                          delete_costs=self.delete_costs, transpose_costs=self.transpose_costs) / max(len(wrong_word), len(candidate))
        log_prior = self.priors[candidate] if candidate in self.priors else math.log(
            float(self.k) / self.N)
        return -dl_dist + self.lamda * log_prior

    def __rankCandidates(self, wrong_word, candidates):
        return [(candidate, self.__score(wrong_word, candidate)) for candidate in candidates]

    def correct(self, wrong_word, top_k=3):
        candidates = self.__generateCandidates(wrong_word)
        scores = self.__rankCandidates(wrong_word, candidates)
        return sorted(scores, key=lambda x: -x[1])[:top_k]
