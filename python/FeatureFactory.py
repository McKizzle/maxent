import json, sys
import base64
from Datum import Datum
import re
import os

class FeatureFactory:
    """
    Add any necessary initialization steps for your features here
    Using this constructor is optional. Depending on your
    features, you may not need to intialize anything.
    """
    def __init__(self):
        self.honorifics_abbr = self.load_list('honorifics-abbr.txt')
        self.honorifics = self.load_list('honorifics.txt')
        self.names = self.load_list('babynames.txt')
        self.weekdays = set(['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                             'Thursday', 'Friday', 'Saturday'])

    def load_list(self, data_filename):
        """Loads a ../data/<data_filename> text file into a set."""
        fn = os.path.join(os.path.dirname(__file__), '../data', data_filename)
        fh = open(fn, 'r')
        s = set(map(lambda str: str.strip().lower(), fh.readlines()))
        fh.close()

        return s

    """
    Words is a list of the words in the entire corpus, previousLabel is the label
    for position-1 (or O if it's the start of a new sentence), and position
    is the word you are adding features for. PreviousLabel must be the
    only label that is visible to this method.
    """

    def computeFeatures(self, words, previousLabel, position):
        features = []
        current_word = words[position]

        """ Baseline Features """
        features.append("word=" + current_word)
        features.append("prevLabel=" + previousLabel)
        features.append("word=" + current_word + ", prevLabel=" + previousLabel)
	"""
        Warning: If you encounter "line search failure" error when
        running the program, considering putting the baseline features
	back. It occurs when the features are too sparse. Once you have
        added enough features, take out the features that you don't need.
	"""

        # leading capital
        if current_word[0].isupper():
            # Irish names
            if re.match(r"(O\'|Mc)[A-Z]{1}[a-z]+", current_word):
                features.append('name=last-irish')

            if current_word.isupper():
                # Maybe it's an abbreviation, like J. Doe (there are 364 of
                # these in the datasets)
                if len(current_word) == 2 and current_word[-1] == '.':
                    features.append('name=first-initial')

                # Sometimes, we just shout names (163 of them)
                features.append('case=caps')
            else:
                # It's not in all caps
                features.append('case=title')

                # Are we looking at a lastname?
                if previousLabel == 'PERSON':
                    features.append('name=last')

        # Is it a name we know?
        if current_word.lower() in self.names:
            features.append('name=known')

        #
        # Looking to the past for answers...
        #
        if position > 0:
            prev_word = words[position - 1].lower()

            # If the previous word was an honorific abbreviation
            if prev_word in self.honorifics:
                features.append('prev=honorific-abbr')

            # If the previous word was a full honorific
            if current_word[0].isupper():
                if prev_word in self.honorifics:
                    features.append('prev=honorific-full')

        return features

    """ Do not modify this method """
    def readData(self, filename):
        data = []

        for line in open(filename, 'r'):
            line_split = line.split()
            # remove emtpy lines
            if len(line_split) < 2:
                continue
            word = line_split[0]
            label = line_split[1]

            datum = Datum(word, label)
            data.append(datum)

        return data

    """ Do not modify this method """
    def readTestData(self, ch_aux):
        data = []

        for line in ch_aux.splitlines():
            line_split = line.split()
            # remove emtpy lines
            if len(line_split) < 2:
                continue
            word = line_split[0]
            label = line_split[1]

            datum = Datum(word, label)
            data.append(datum)

        return data


    """ Do not modify this method """
    def setFeaturesTrain(self, data):
        newData = []
        words = []

        for datum in data:
            words.append(datum.word)

        ## This is so that the feature factory code doesn't
        ## accidentally use the true label info
        previousLabel = "O"
        for i in range(0, len(data)):
            datum = data[i]

            newDatum = Datum(datum.word, datum.label)
            newDatum.features = self.computeFeatures(words, previousLabel, i)
            newDatum.previousLabel = previousLabel
            newData.append(newDatum)

            previousLabel = datum.label

        return newData

    """
    Compute the features for all possible previous labels
    for Viterbi algorithm. Do not modify this method
    """
    def setFeaturesTest(self, data):
        newData = []
        words = []
        labels = []
        labelIndex = {}

        for datum in data:
            words.append(datum.word)
            if not labelIndex.has_key(datum.label):
                labelIndex[datum.label] = len(labels)
                labels.append(datum.label)

        ## This is so that the feature factory code doesn't
        ## accidentally use the true label info
        for i in range(0, len(data)):
            datum = data[i]

            if i == 0:
                previousLabel = "O"
                datum.features = self.computeFeatures(words, previousLabel, i)

                newDatum = Datum(datum.word, datum.label)
                newDatum.features = self.computeFeatures(words, previousLabel, i)
                newDatum.previousLabel = previousLabel
                newData.append(newDatum)
            else:
                for previousLabel in labels:
                    datum.features = self.computeFeatures(words, previousLabel, i)

                    newDatum = Datum(datum.word, datum.label)
                    newDatum.features = self.computeFeatures(words, previousLabel, i)
                    newDatum.previousLabel = previousLabel
                    newData.append(newDatum)

        return newData

    """
    write words, labels, and features into a json file
    Do not modify this method
    """
    def writeData(self, data, filename):
        outFile = open(filename + '.json', 'w')
        for i in range(0, len(data)):
            datum = data[i]
            jsonObj = {}
            jsonObj['_label'] = datum.label
            jsonObj['_word']= base64.b64encode(datum.word)
            jsonObj['_prevLabel'] = datum.previousLabel

            featureObj = {}
            features = datum.features
            for j in range(0, len(features)):
                feature = features[j]
                featureObj['_'+feature] = feature
            jsonObj['_features'] = featureObj

            outFile.write(json.dumps(jsonObj) + '\n')

        outFile.close()
