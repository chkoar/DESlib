import pytest
from sklearn.linear_model import Perceptron
from deslib.des.knop import KNOP
from deslib.tests.examples_test import *


@pytest.mark.parametrize('index, expected', [(0, [4.0, 3.0, 4.0]),
                                             (1, [5.0, 2.0, 5.0]),
                                             (2, [2.0, 5.0, 2.0])])
def test_estimate_competence(index, expected):
    query = np.atleast_2d([1, 1])

    knop_test = KNOP(create_pool_classifiers())
    knop_test.fit(X_dsel_ex1, y_dsel_ex1)

    knop_test.DFP_mask = np.ones(knop_test .n_classifiers)
    knop_test.neighbors = neighbors_ex1[index, :]
    knop_test.distances = distances_ex1[index, :]
    competences = knop_test.estimate_competence(query)
    assert np.allclose(competences, expected, atol=0.01)


# Test the estimate competence method receiving n samples as input
def test_estimate_competence_batch():
    query = np.ones((3, 2))
    expected = np.array([[4.0, 3.0, 4.0],
                          [5.0, 2.0, 5.0],
                          [2.0, 5.0, 2.0]])

    knop_test = KNOP(create_pool_classifiers())
    knop_test.fit(X_dsel_ex1, y_dsel_ex1)

    knop_test.DFP_mask = np.ones(knop_test .n_classifiers)
    knop_test.neighbors = neighbors_ex1
    knop_test.distances = distances_ex1
    competences = knop_test.estimate_competence(query)
    assert np.allclose(competences, expected, atol=0.01)


@pytest.mark.parametrize('index, expected', [(0, 0),
                                             (1, 0),
                                             (2, 1)])
def test_classify(index, expected):
    query = np.atleast_2d([1, 1])

    knop_test = KNOP(create_pool_classifiers())
    knop_test.fit(X_dsel_ex1, y_dsel_ex1)

    knop_test.DFP_mask = np.ones(knop_test .n_classifiers)
    knop_test.neighbors = neighbors_ex1[index, :]
    knop_test.distances = distances_ex1[index, :]

    predictions = []
    for clf in knop_test.pool_classifiers:
        predictions.append(clf.predict(query)[0])

    predicted_label = knop_test.classify_instance(query, np.array(predictions))

    assert predicted_label == expected


# Test the classify method receiving multiple samples as input
def test_classify_batch():
    query = np.ones((3, 2))
    expected = np.array([0, 0, 1])
    knop_test = KNOP(create_pool_classifiers())
    knop_test.fit(X_dsel_ex1, y_dsel_ex1)

    knop_test.DFP_mask = np.ones(knop_test .n_classifiers)
    knop_test.neighbors = neighbors_ex1
    knop_test.distances = distances_ex1

    predictions = []
    for clf in knop_test.pool_classifiers:
        predictions.append(clf.predict(query)[0])

    predicted_label = knop_test.classify_instance(query, np.array(predictions))

    assert np.equal(predicted_label, expected)


def test_weights_zero():
    query = np.atleast_2d([1, 1])

    knop_test = KNOP(create_pool_classifiers())
    knop_test.fit(X_dsel_ex1, y_dsel_ex1)

    knop_test.estimate_competence = MagicMock(return_value=np.zeros(3))

    result = knop_test.select(query)
    assert np.array_equal(result, np.array([0, 1, 0]))


def test_fit():
    knop_test = KNOP(create_pool_classifiers())
    knop_test.fit(X_dsel_ex1, y_dsel_ex1)
    expected_scores = np.ones((15, 6)) * np.array([0.5, 0.5, 1.0, 0.0, 0.33, 0.67])
    assert np.array_equal(expected_scores, knop_test.dsel_scores)
    # Assert the roc_algorithm is fitted to the scores (decision space) rather than the features (feature space)
    assert np.array_equal(knop_test.roc_algorithm._fit_X, knop_test.dsel_scores)


# Test if the class is raising an error when the base classifiers do not implements the predict_proba method.
# Should raise an exception when the base classifier cannot estimate posterior probabilities (predict_proba)
# Using Perceptron classifier as it does not implements the predict_proba method.
def test_not_predict_proba():
    X = X_dsel_ex1
    y = y_dsel_ex1
    clf1 = Perceptron()
    clf1.fit(X, y)
    with pytest.raises(ValueError):
        KNOP([clf1, clf1])


