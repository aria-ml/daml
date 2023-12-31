from typing import Optional

import alibi_detect
import numpy as np
from alibi_detect.models.tensorflow.autoencoder import VAEGMM

from daml._internal.metrics.alibi_detect.base import _AlibiDetectMetric


class AlibiVAEGMM(_AlibiDetectMetric):
    """
    Variational Gaussian Mixture Model Autoencoder-based outlier detector,
    using `alibi-detect vaegmm. <https://docs.seldon.io/projects/alibi-detect/en/latest/od/methods/vaegmm.html>`_


    The model used by this class is :py:class:`daml.models.VAEGMM`
    """  # noqa E501

    def __init__(self, model: Optional[VAEGMM] = None):
        super().__init__(
            alibi_detect_class=alibi_detect.od.OutlierVAEGMM,
            model_class=VAEGMM,
            model_param_name="vaegmm",
            model=model,
            flatten_dataset=True,
            dataset_type=np.float32,
        )

    def set_prediction_args(
        self,
        return_instance_score: Optional[bool] = None,
    ) -> None:
        """
        Sets additional arguments to be used during prediction.

        Note
        ----
        Visit `alibi-detect vaegmm <https://docs.seldon.io/projects/alibi-detect/en/latest/od/methods/vaegmm.html#Detect>`_ for additional information on prediction parameters.
        """  # noqa E501
        self._update_kwargs_with_locals(self._predict_kwargs, **locals())

    @property
    def _default_predict_kwargs(self) -> dict:
        return {"return_instance_score": True, "batch_size": 64}
