import numpy as np
import pytest

from daml.datasets import DamlDataset
from daml.metrics.uap import UAPOutput
from daml.metrics.uap.aria import UAP


class TestUAP:
    @pytest.mark.parametrize(
        "input, output",
        [
            (UAP, UAPOutput(uap=1.0)),
        ],
    )
    def test_multiclass_UAP_with_mnist(self, input, output):
        """
        Load a slice of the MNIST dataset and pass into the UAP
        evaluate function.
        """

        path = "tests/datasets/mnist.npz"
        with np.load(path, allow_pickle=True) as fp:
            covariates, labels = fp["x_train"][:1000], fp["y_train"][:1000]
        dataset = DamlDataset(covariates, labels)
        metric = input()
        value = metric.evaluate(dataset)
        assert value == output
