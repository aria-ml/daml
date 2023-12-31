"""
This module contains the implementation of the
FR Test Statistic based estimate and the
FNN based estimate for the Bayes Error Rate
"""
from abc import abstractmethod
from typing import Tuple

import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial.distance import pdist, squareform

from daml._internal.datasets.datasets import DamlDataset
from daml._internal.metrics.aria.base import _AriaMetric
from daml._internal.metrics.outputs import BEROutput


class _MultiClassBer(_AriaMetric):
    def __init__(self, encode: bool = False) -> None:
        """Constructor method"""

        super().__init__(encode)

    @abstractmethod
    def _multiclass_ber(
        self,
        X: np.ndarray,
        y: np.ndarray,
    ) -> Tuple[float, float]:
        pass

    def _get_classes_counts(self, labels: np.ndarray) -> Tuple[int, np.intp]:
        classes, counts = np.unique(labels, return_counts=True)
        M = len(classes)
        if M < 2:
            raise ValueError("Label vector contains less than 2 classes!")
        if M > 10:
            raise ValueError("Label vector contains more than 10 classes!")
        N = np.sum(counts)
        return M, N

    def evaluate(self, dataset: DamlDataset) -> BEROutput:
        """
        Return the Bayes Error Rate estimate

        Parameters
        ----------
        dataset : DamlDataset
            Dataset containing (n_samples x n_features) array of (padded) instance
            embeddings and n_samples vector of class labels with M unique classes.
        Returns
        -------
        BEROutput
            The estimated upper and lower bounds of the Bayes Error Rate

        Raises
        ------
        ValueError
            If unique classes M < 2 or M > 10

        See Also
        --------
        https://gitlab.jatic.net/jatic/aria/daml/-/issues/83
        """
        X: np.ndarray = dataset.images
        y: np.ndarray = dataset.labels

        # If self.encode == True, pass X through an autoencoder before evaluating BER
        if self.encode:
            if not self._is_trained or self.autoencoder is None:
                raise TypeError(
                    "Tried to encode data without fitting a model.\
                    Try calling Metric.fit_dataset(dataset) first."
                )
            else:
                X = self.autoencoder.encoder.predict(X)

        ber, ber_lower = self._multiclass_ber(X, y)
        return BEROutput(ber=ber, ber_lower=ber_lower)


class MultiClassBerMST(_MultiClassBer):
    """
    Implements the FR Test Statistic based estimator for the Bayes Error Rate

    Note
    ----
    `Learning to Bound the Multi-class Bayes Error (Th. 3 and Th. 4) <https://arxiv.org/abs/1811.06419>`_
    """  # noqa F401

    def _multiclass_ber(
        self,
        X: np.ndarray,
        y: np.ndarray,
    ) -> Tuple[float, float]:
        """
        Calculates the Bayes Error Rate estimate

        Parameters
        ----------
        X : np.ndarray
            (n_samples x n_features) array of covariates (or image embeddings)
        y : np.ndarray
            n_samples vector of class labels with M unique classes. 2 <= M <= 10

        Returns
        -------
        float
            Estimate of the Bayes Error Rate

        Raises
        ------
        ValueError
            If unique classes M < 2 or M > 10
        """
        M, N = self._get_classes_counts(y)

        # All features belong on second dimension
        X = X.reshape((X.shape[0], -1))
        # We add a small constant to the distance matrix to ensure scipy interprets
        # the input graph as fully-connected.
        dense_eudist = squareform(pdist(X)) + 1e-4
        eudist_csr = csr_matrix(dense_eudist)
        tree = coo_matrix(minimum_spanning_tree(eudist_csr))
        sum = np.sum([y[tree.row[i]] != y[tree.col[i]] for i in range(N - 1)])
        deltas = sum / (2 * N)
        upper = 2 * deltas
        lower = ((M - 1) / (M)) * (1 - (1 - 2 * ((M) / (M - 1)) * deltas) ** 0.5)
        return upper, lower


class MultiClassBerFNN(_MultiClassBer):
    """
    Implements the KNN Test Statistic based estimator for the Bayes Error Rate

    Parameters
    ----------
    X : np.ndarray
        (n_samples x n_features) array of covariates (or image embeddings)
    y : np.ndarray
        n_samples vector of class labels with M unique classes. 2 <= M <= 10

    Returns
    -------
    float
        Estimate of the Bayes Error Rate

    Raises
    ------
    ValueError
        If unique classes M < 2 or M > 10

    See Also
    --------
    `Learning to Bound the Multi-class Bayes Error (Th. 3 and Th. 4) <https://arxiv.org/abs/1811.06419>`_
    """  # noqa F401

    def _multiclass_ber(
        self,
        X: np.ndarray,
        y: np.ndarray,
    ) -> Tuple[float, float]:
        M, N = self._get_classes_counts(y)

        # All features belong on second dimension
        X = X.reshape((X.shape[0], -1))
        nn_indices = self._compute_neighbors(X, X)
        deltas = float(np.count_nonzero(y[nn_indices] - y) / (2 * N))
        upper = 2 * deltas
        lower = ((M - 1) / (M)) * (1 - (1 - 2 * ((M) / (M - 1)) * deltas) ** 0.5)
        return upper, lower
