from dedupe.api import Dedupe
from dedupe.labeler import ActiveLearner, DisagreementLearner, BlockLearner, RLRLearner
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm.classes import SVC, LinearSVC

import numpy
import random


class SVMLearner(RLRLearner):

    def __init__(self, data_model):
        super().__init__(data_model)

        self.svm = SVC(kernel='linear', probability=True, tol=0.0001)

    def fit_transform(self, pairs, y):
        y = numpy.array(y)
        if not y.any():
            random_pair = random.choice(self.candidates)
            exact_match = (random_pair[0], random_pair[0])
            pairs = pairs + [exact_match]
            y = numpy.concatenate([y, [1]])
        elif numpy.count_nonzero(y) == len(y):
            random_pair = random.choice(self.candidates)
            pairs = pairs + [random_pair]
            y = numpy.concatenate([y, [0]])

        super().fit_transform(pairs, y)

    def fit(self, X, y):
        self.svm.fit(X, y)

    def predict_proba(self, examples):
        return self.svm.predict_proba(examples)[:, 1].reshape(-1, 1)


class SVMDisagreementLearner(DisagreementLearner):

    def __init__(self, data_model):
        self.data_model = data_model

        self.classifier = SVMLearner(data_model)
        self.blocker = BlockLearner(data_model)

        self.learners = (self.classifier, self.blocker)
        self.y = numpy.array([])
        self.pairs = []

    #     self.pop_from_disagreement = True

    # def pop(self):
    #     if self.pop_from_disagreement:
    #         [uncertain_pair] = super().pop()
    #     else:
    #         [uncertain_pair] = self.classifier.pop()
    #         try:
    #             self.blocker.remove(uncertain_pair)
    #         except ValueError:
    #             self.blocker.remove((uncertain_pair[1], uncertain_pair[0]))

    #     self.pop_from_disagreement = not self.pop_from_disagreement
    #     return [uncertain_pair]


class SVMDedupe(Dedupe):
    classifier = SVC(kernel='linear', probability=True, tol=0.0001)
    ActiveLearner = SVMDisagreementLearner
