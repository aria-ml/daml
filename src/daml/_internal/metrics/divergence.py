"""
This module contains the implementation of Dp Divergence
using the Fast Nearest Neighbor and Minimum Spanning Tree algorithms
"""

from typing import Callable, Dict, Literal

import numpy as np

from daml._internal.metrics.base import EvaluateMixin, MethodsMixin
from daml._internal.metrics.outputs import DivergenceOutput

from .utils import compute_neighbors, minimum_spanning_tree


def _mst(data: np.ndarray, labels: np.ndarray) -> int:
    mst = minimum_spanning_tree(data).toarray()
    edgelist = np.transpose(np.nonzero(mst))
    errors = np.sum(labels[edgelist[:, 0]] != labels[edgelist[:, 1]])
    return errors


def _fnn(data: np.ndarray, labels: np.ndarray) -> int:
    nn_indices = compute_neighbors(data, data)
    errors = np.sum(np.abs(labels[nn_indices] - labels))
    return errors


class Divergence(EvaluateMixin, MethodsMixin[Callable[[np.ndarray, np.ndarray], int]]):
    """
    Calculates the estimated divergence between two datasets

    Parameters
    ----------
    data_a : np.ndarray
        Array of images or image embeddings to compare
    data_b : np.ndarray
        Array of images or image embeddings to compare

    See Also
    --------
        For more information about this divergence, its formal definition,
        and its associated estimators see https://arxiv.org/abs/1412.6534.

    Warning
    -------
        MST is very slow in this implementation, this is unlike matlab where
        they have comparable speeds
        Overall, MST takes ~25x LONGER!!
        Source of slowdown:
        conversion to and from CSR format adds ~10% of the time diff between
        1nn and scipy mst function the remaining 90%
    """

    def __init__(
        self,
        data_a: np.ndarray,
        data_b: np.ndarray,
        method: Literal["FNN", "MST"] = "FNN",
    ) -> None:
        self.data_a = data_a
        self.data_b = data_b
        self.method = method

    @classmethod
    def _methods(cls) -> Dict[str, Callable[[np.ndarray, np.ndarray], int]]:
        return {"FNN": _fnn, "MST": _mst}

    def evaluate(self) -> DivergenceOutput:
        """
        Calculates the divergence and any errors between the datasets

        Returns
        -------
        DivergenceOutput
            Dataclass containing the dp divergence and errors during calculation
        """
        N = self.data_a.shape[0]
        M = self.data_b.shape[0]

        stacked_data = np.vstack((self.data_a, self.data_b))
        labels = np.vstack([np.zeros([N, 1]), np.ones([M, 1])])

        errors = self.method(stacked_data, labels)
        dp = max(0.0, 1 - ((M + N) / (2 * M * N)) * errors)
        return DivergenceOutput(dpdivergence=dp, error=errors)
