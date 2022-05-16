import pyiwn
import re

#Download the IndoWordnet synset data
#pyiwn.download()

#Create a IndoWordNet class instance and set a language to access its Wordnet
iwn = pyiwn.IndoWordNet(pyiwn.Language.BENGALI)
import preprocess
from itertools import chain






# Reference: For simple lesk and adapted lesk: https://github.com/alvations/pywsd,
# For  Original Lesk and basic code framework: https://www.kaggle.com/antriksh5235/semantic-similarity-using-wordnet
class Lesk(object):

	def __init__(self, sentence, simple=True, adapted=False):
		self.sentence = sentence
		self.meanings = {}
		self.simple_lesk = simple,
		self.adapted_lesk = adapted
		for word in sentence:
			self.meanings[word] = ''

	def getSenses(self, word):
		"""
		:param word: Type: String, word whose synsets are required.
		:return: Returns a list of Synset objects for the given word if present in the IndoWordNet else returns an empty list.
		"""
		try:
			return iwn.synsets(word)
		except:
			return []

	def getGloss(self, senses):
		"""
		:param senses: a list of Synset objects for the given word from the IndoWordNet.
		:return: Type: dictionary where key is of the form <lemma>.<POS>.<SYNSET_ID> and value contains the defintion of the corresponding synset.
		"""

		dl = preprocess.Document_linearization()

		gloss = {}

		for sense in senses:
			gloss[sense] = []

		for sense in senses:
			gloss[sense] += dl.pre_process(sense.gloss())
			if self.simple_lesk:
				# Adds the examples and lemma names.
				gloss[sense] += chain(*[dl.pre_process(eg) for eg in sense.examples()])
				gloss[sense] += sense.lemma_names()

				# Includes lemma_names of hyper-/hyponyms.
				hyperhyponyms = set(
					iwn.synset_relation(sense, pyiwn.SynsetRelations.HYPONYMY) + iwn.synset_relation(sense,
																									 pyiwn.SynsetRelations.HYPERNYMY))
				gloss[sense] += set(chain(*[i.lemma_names() for i in hyperhyponyms]))

			if self.adapted_lesk:
				# Includes lemma_names from holonyms, meronyms and similar
				related_senses = set(
					iwn.synset_relation(sense, pyiwn.SynsetRelations.HOLO_PORTION_MASS) + iwn.synset_relation(sense,
																											  pyiwn.SynsetRelations.HOLO_COMPONENT_OBJECT) + iwn.synset_relation(
						sense, pyiwn.SynsetRelations.HOLO_PLACE_AREA) + \
					iwn.synset_relation(sense, pyiwn.SynsetRelations.HOLO_FEATURE_ACTIVITY) + iwn.synset_relation(sense,
																												  pyiwn.SynsetRelations.HOLO_MEMBER_COLLECTION) + iwn.synset_relation(
						sense, pyiwn.SynsetRelations.HOLO_POSITION_AREA) + iwn.synset_relation(sense,
																							   pyiwn.SynsetRelations.HOLO_STUFF_OBJECT) + \
					iwn.synset_relation(sense, pyiwn.SynsetRelations.MERO_MEMBER_COLLECTION) + iwn.synset_relation(
						sense, pyiwn.SynsetRelations.MERO_COMPONENT_OBJECT) + iwn.synset_relation(sense,
																								  pyiwn.SynsetRelations.MERO_FEATURE_ACTIVITY) + \
					iwn.synset_relation(sense, pyiwn.SynsetRelations.MERO_PORTION_MASS) + iwn.synset_relation(sense,
																											  pyiwn.SynsetRelations.MERO_STUFF_OBJECT) + iwn.synset_relation(
						sense, pyiwn.SynsetRelations.MERO_POSITION_AREA) + iwn.synset_relation(sense,
																							   pyiwn.SynsetRelations.MERO_PLACE_AREA) + \
					iwn.synset_relation(sense, pyiwn.SynsetRelations.SIMILAR))
				gloss[sense] += set(chain(*[i.lemma_names() for i in related_senses]))

		return gloss

	def getAllGlosses(self, word):
		"""
		:param word: Type String, contains a single word
		:return: Returns a dictionary of all the Gloss definition of each of the senses of the word depending upon the type of lesk chosen.
				 If the word is not present in the IndoWordNet it returns an empty list.
		"""
		senses = self.getSenses(word)

		if senses == []:
			return {word: senses}
		return self.getGloss(senses)

	def Score(self, sense_bag, context_bag):
		# Base
		overlap = 0

		# Step
		for word in sense_bag:
			if word in context_bag:
				overlap += 1

		return overlap

	def overlapScore(self, ambiguous_word, context_word):
		"""
		Finds the sense of the ambiguous word having maximum overlap with senses of the context word.
		:param ambiguous_word: String, word which has to be disambiguated
		:param context_word: String, context word from the sentence
		:return: Returns the predicted sense of the ambiguous word along with the maximum overlap score.
		"""

		ambiguous_gloss_set = self.getAllGlosses(ambiguous_word)
		if self.meanings[context_word] == '':
			context_gloss_set = self.getAllGlosses(context_word)
		else:
			context_gloss_set = self.getGloss([self.meanings[context_word]])

		score = {}
		for i in ambiguous_gloss_set.keys():
			score[i] = 0
			for j in context_gloss_set.keys():
				score[i] += self.Score(ambiguous_gloss_set[i], context_gloss_set[j])

		bestSense = None
		max_score = 0
		for i in ambiguous_gloss_set.keys():
			if score[i] > max_score:
				max_score = score[i]
				bestSense = i

		return bestSense, max_score

	def get_sense_name(self, result):
		# The output is of the form Synset('lemma.pos.synset_id') so we clean the output to get only lemma.pos.synset_id
		result = re.sub(r"['()']+\ *", '', str(result))
		result = result.replace('Synset', "")
		return result

	def lesk(self, word, sentence):

		context = sentence
		meaning = {}

		senses = self.getSenses(word)
		for sense in senses:
			meaning[sense] = 0

		for context_word in context:
			if not word == context_word:
				score = self.overlapScore(word, context_word)
				if score[0] == None:
					continue
				# Finds the total overlap score of every sense of the ambiguous word with respect to each of the senses in the context bag.
				meaning[score[0]] += score[1]

		if senses == []:
			return None

		# Finds the sense of the ambiguous word having maximum overlap with senses of the context bag (entire sentence).
		self.meanings[word] = max(meaning.keys(), key=lambda x: meaning[x])

		return self.meanings[word]

