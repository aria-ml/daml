import numpy as np
import pytest

from daml.metrics.outlier_detection import AE, AEGMM, LLR, VAE, VAEGMM

from .utils import MockImageClassificationGenerator


@pytest.mark.parametrize(
    "method",
    [
        AE,
        AEGMM,
        VAE,
        VAEGMM,
        # remove functional marker after issue #94 is resolved
        pytest.param(LLR, marks=pytest.mark.functional),
    ],
)
class Test:
    # Test main functionality of the program
    @pytest.mark.functional
    def test_label_5s_as_outliers(self, method):
        """Functional testing of  OutlierDection

        The AE model is being trained on all 1's and tested on all 5's.
        When evaluating, the model should say all 1's are not outliers
        and all 5's are outliers
        """

        input_shape = (32, 32, 3)

        # Initialize a dataset of 32 images of size 32x32x3, containing all 1's
        all_ones = MockImageClassificationGenerator(
            limit=1, labels=1, img_dims=input_shape
        )

        # Initialize a dataset of 32 images of size 32x32x3, containing all 5's
        all_fives = MockImageClassificationGenerator(
            limit=1, labels=5, img_dims=input_shape
        )

        # Get model input from each dataset
        X_all_ones = all_ones.dataset.images
        X_all_fives = all_fives.dataset.images

        # Initialize the autoencoder-based outlier detector from alibi-detect
        metric = method()

        metric.initialize_detector(input_shape)

        # TODO Need to create a helper function to handle this
        if metric._DATASET_TYPE is not None:
            X_all_ones = X_all_ones.astype(metric._DATASET_TYPE)
            X_all_fives = X_all_fives.astype(metric._DATASET_TYPE)

        # Train the detector on the dataset of all 1's
        metric.fit_dataset(dataset=X_all_ones, epochs=10, verbose=False)

        # Evaluate the detector on the dataset of all 1's
        preds_on_ones = metric.evaluate(X_all_ones).is_outlier
        # print(preds_on_ones)
        # ones_outliers = preds_on_ones
        # Evaluate the detector on the dataset of all 5's
        preds_on_fives = metric.evaluate(X_all_fives).is_outlier
        # fives_outliers = preds_on_fives

        # We expect all elements to not be outliers
        num_errors_on_ones = np.sum(np.where(preds_on_ones != 0))
        # We expect all elements to be outliers
        num_errors_on_fives = np.sum(np.where(preds_on_fives != 1))

        assert len(preds_on_ones) == len(X_all_ones)
        assert len(preds_on_fives) == len(X_all_fives)

        assert num_errors_on_ones == 0
        assert num_errors_on_fives == 0

    @pytest.mark.functional
    def test_different_input_shape(self, method):
        """Testing of  Detection under different input size"""

        input_shape = (38, 38, 2)

        # Initialize a dataset of 32 images of size 32x32x3, containing all 1's
        all_ones = MockImageClassificationGenerator(
            limit=1, labels=1, img_dims=input_shape
        )

        # Get model input from each dataset
        X_all_ones = all_ones.dataset.images

        metric = method()

        # Initialize the autoencoder-based outlier detector from alibi-detect
        metric.initialize_detector(input_shape)

        # TODO Need to create a helper function to handle this
        if metric._DATASET_TYPE is not None:
            X_all_ones = X_all_ones.astype(metric._DATASET_TYPE)

        # Train the detector on the dataset of all 1's
        metric.fit_dataset(dataset=X_all_ones, epochs=10, verbose=False)

        # Evaluate the detector on the dataset of all 1's
        preds_on_ones = metric.evaluate(X_all_ones).is_outlier

        num_errors_on_ones = np.sum(np.where(preds_on_ones != 0))

        assert num_errors_on_ones == 0

    # Ensure that the program fails upon wrong order of operations
    def test_eval_before_fit_fails(self, method):
        """Testing incorrect order of operations for fitting and evaluating"""

        input_shape = (32, 32, 3)

        all_ones = MockImageClassificationGenerator(
            limit=3, labels=1, img_dims=input_shape
        )

        X = all_ones.dataset.images

        metric = method()

        metric.initialize_detector(input_shape)

        # force metric.is_trained = False
        # Evaluate dataset before fitting it
        with pytest.raises(TypeError):
            metric.evaluate(X)

    # Ensure that the program fails upon testing on a dataset of different
    # shape than what was trained on
    def test_wrong_dataset_dims_fails(self, method):
        """Testing incorrect order of operations for fitting and evaluating"""

        input_shape = (32, 32, 3)
        faulty_input_shape = (11, 32, 3)

        all_ones = MockImageClassificationGenerator(
            limit=3, labels=1, img_dims=input_shape[:1], channels=input_shape[2]
        )

        faulty_all_ones = MockImageClassificationGenerator(
            limit=3,
            labels=1,
            img_dims=faulty_input_shape[:1],
            channels=faulty_input_shape[2],
        )

        X = all_ones.dataset.images
        faulty_X = faulty_all_ones.dataset.images

        metric = method()

        if metric._DATASET_TYPE is not None:
            X = X.astype(metric._DATASET_TYPE)
            faulty_X = faulty_X.astype(metric._DATASET_TYPE)

        metric.initialize_detector(input_shape)

        metric.fit_dataset(dataset=X, epochs=1, verbose=False)

        # force
        # metric.is_trained = False
        # Evaluate dataset before fitting it
        with pytest.raises(TypeError):
            metric.evaluate(faulty_X)

    def test_missing_detector(self, method):
        input_shape = (32, 32, 3)

        all_ones = MockImageClassificationGenerator(
            limit=1, labels=1, img_dims=input_shape
        )

        X = all_ones.dataset.images

        metric = method()

        with pytest.raises(TypeError):
            metric.fit_dataset(dataset=X, epochs=1, verbose=False)

        with pytest.raises(TypeError):
            metric.evaluate(dataset=X)
