from typing import Literal, Optional, Tuple

import numpy as np
import pytest

from tests.utils.datasets import download_mnist


def pytest_addoption(parser):
    parser.addoption(
        "--runfunctional",
        action="store_true",
        default=False,
        help="run functional tests",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runfunctional"):
        # --runfunctional given in cli: do not skip slow tests
        return
    skip_func = pytest.mark.skip(reason="need --runfunctional option to run")
    for item in items:
        if "functional" in item.keywords:
            item.add_marker(skip_func)


@pytest.fixture
def mnist():
    def _method(
        size: int = 1000,
        category: Literal["train", "test"] = "train",
        dtype: Optional[type] = None,
        add_channels: Literal["channels_first", "channels_last", "none"] = "none",
    ) -> Tuple[np.ndarray, np.ndarray]:
        path = download_mnist()
        with np.load(path, allow_pickle=True) as fp:
            images, labels = fp["x_" + category][:size], fp["y_" + category][:size]
        if dtype is not None:
            images = images.astype(dtype)
        if add_channels == "channels_last":
            images = images[..., np.newaxis]
        elif add_channels == "channels_first":
            images = images[:, np.newaxis]
        return images, labels

    return _method
