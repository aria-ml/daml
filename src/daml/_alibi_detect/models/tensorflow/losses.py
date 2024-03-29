from typing import Optional

import tensorflow as tf
import tensorflow_probability as tfp
from tensorflow.keras.layers import Flatten
from tensorflow.keras.losses import categorical_crossentropy, kld

from daml._alibi_detect.models.tensorflow.gmm import gmm_energy, gmm_params


def elbo(
    y_true: tf.Tensor,
    y_pred: tf.Tensor,
    cov_full: Optional[tf.Tensor] = None,
    cov_diag: Optional[tf.Tensor] = None,
    sim: Optional[float] = None,
) -> tf.Tensor:
    """
    Compute ELBO loss. The covariance matrix can be specified by passing the full covariance matrix, the matrix
    diagonal, or a scale identity multiplier. Only one of these should be specified. If none are specified, the
    identity matrix is used.

    Parameters
    ----------
    y_true
        Labels.
    y_pred
        Predictions.
    cov_full
        Full covariance matrix.
    cov_diag
        Diagonal (variance) of covariance matrix.
    sim
        Scale identity multiplier.

    Returns
    -------
    ELBO loss value.

    Example
    -------
    >>> import tensorflow as tf
    >>> from alibi_detect.models.tensorflow.losses import elbo
    >>> y_true = tf.constant([[0.0, 1.0], [1.0, 0.0]])
    >>> y_pred = tf.constant([[0.1, 0.9], [0.8, 0.2]])
    >>> # Specifying scale identity multiplier
    >>> elbo(y_true, y_pred, sim=1.0)
    >>> # Specifying covariance matrix diagonal
    >>> elbo(y_true, y_pred, cov_diag=tf.ones(2))
    >>> # Specifying full covariance matrix
    >>> elbo(y_true, y_pred, cov_full=tf.eye(2))
    """
    if len([x for x in [cov_full, cov_diag, sim] if x is not None]) > 1:
        raise ValueError("Only one of cov_full, cov_diag or sim should be specified.")

    y_pred_flat = Flatten()(y_pred)
    if isinstance(cov_full, tf.Tensor):
        y_mn = tfp.distributions.MultivariateNormalFullCovariance(
            y_pred_flat, covariance_matrix=cov_full
        )
    else:
        if sim:
            cov_diag = sim * tf.ones(y_pred_flat.shape[-1])
        y_mn = tfp.distributions.MultivariateNormalDiag(
            y_pred_flat, scale_diag=cov_diag
        )
    loss = -tf.reduce_mean(y_mn.log_prob(Flatten()(y_true)))
    return loss


def loss_aegmm(
    x_true: tf.Tensor,
    x_pred: tf.Tensor,
    z: tf.Tensor,
    gamma: tf.Tensor,
    w_energy: float = 0.1,
    w_cov_diag: float = 0.005,
) -> tf.Tensor:
    """
    Loss function used for OutlierAEGMM.

    Parameters
    ----------
    x_true
        Batch of instances.
    x_pred
        Batch of reconstructed instances by the autoencoder.
    z
        Latent space values.
    gamma
        Membership prediction for mixture model components.
    w_energy
        Weight on sample energy loss term.
    w_cov_diag
        Weight on covariance regularizing loss term.

    Returns
    -------
    Loss value.
    """
    recon_loss = tf.reduce_mean((x_true - x_pred) ** 2)
    phi, mu, cov, L, log_det_cov = gmm_params(z, gamma)
    sample_energy, cov_diag = gmm_energy(
        z, phi, mu, cov, L, log_det_cov, return_mean=True
    )
    loss = recon_loss + w_energy * sample_energy + w_cov_diag * cov_diag
    return loss


def loss_vaegmm(
    x_true: tf.Tensor,
    x_pred: tf.Tensor,
    z: tf.Tensor,
    gamma: tf.Tensor,
    w_recon: float = 1e-7,
    w_energy: float = 0.1,
    w_cov_diag: float = 0.005,
    cov_full: tf.Tensor = None,
    cov_diag: tf.Tensor = None,
    sim: float = 0.05,
) -> tf.Tensor:
    """
    Loss function used for OutlierVAEGMM.

    Parameters
    ----------
    x_true
        Batch of instances.
    x_pred
        Batch of reconstructed instances by the variational autoencoder.
    z
        Latent space values.
    gamma
        Membership prediction for mixture model components.
    w_recon
        Weight on elbo loss term.
    w_energy
        Weight on sample energy loss term.
    w_cov_diag
        Weight on covariance regularizing loss term.
    cov_full
        Full covariance matrix.
    cov_diag
        Diagonal (variance) of covariance matrix.
    sim
        Scale identity multiplier.

    Returns
    -------
    Loss value.
    """
    recon_loss = elbo(x_true, x_pred, cov_full=cov_full, cov_diag=cov_diag, sim=sim)
    phi, mu, cov, L, log_det_cov = gmm_params(z, gamma)
    sample_energy, cov_diag = gmm_energy(z, phi, mu, cov, L, log_det_cov)
    loss = w_recon * recon_loss + w_energy * sample_energy + w_cov_diag * cov_diag
    return loss


def loss_adv_ae(
    x_true: tf.Tensor,
    x_pred: tf.Tensor,
    model: tf.keras.Model = None,
    model_hl: list = None,
    w_model: float = 1.0,
    w_recon: float = 0.0,
    w_model_hl: list = None,
    temperature: float = 1.0,
) -> tf.Tensor:
    """
    Loss function used for AdversarialAE.

    Parameters
    ----------
    x_true
        Batch of instances.
    x_pred
        Batch of reconstructed instances by the autoencoder.
    model
        A trained tf.keras model with frozen layers (layers.trainable = False).
    model_hl
        List with tf.keras models used to extract feature maps and make predictions on hidden layers.
    w_model
        Weight on model prediction loss term.
    w_recon
        Weight on MSE reconstruction error loss term.
    w_model_hl
        Weights assigned to the loss of each model in model_hl.
    temperature
        Temperature used for model prediction scaling.
        Temperature <1 sharpens the prediction probability distribution.

    Returns
    -------
    Loss value.
    """
    y_true = model(x_true)
    y_pred = model(x_pred)

    # apply temperature scaling
    if temperature != 1.0:
        y_true = y_true ** (1 / temperature)
        y_true = y_true / tf.reshape(tf.reduce_sum(y_true, axis=-1), (-1, 1))

    # compute K-L divergence loss
    loss_kld = kld(y_true, y_pred)
    std_kld = tf.math.reduce_std(loss_kld)
    loss = tf.reduce_mean(loss_kld)

    # add loss from optional K-L divergences extracted from hidden layers
    if isinstance(model_hl, list):
        if w_model_hl is None:
            w_model_hl = list(tf.ones(len(model_hl)))
        for m, w in zip(model_hl, w_model_hl):
            h_true = m(x_true)
            h_pred = m(x_pred)
            loss_kld_hl = tf.reduce_mean(kld(h_true, h_pred))
            loss += tf.constant(w) * loss_kld_hl
    loss *= w_model

    # add optional reconstruction loss
    if w_recon > 0.0:
        loss_recon = (x_true - x_pred) ** 2
        std_recon = tf.math.reduce_std(loss_recon)
        w_scale = std_kld / (std_recon + 1e-10)
        loss_recon = w_recon * w_scale * tf.reduce_mean(loss_recon)
        loss += loss_recon
        return loss
    else:
        return loss


def loss_distillation(
    x_true: tf.Tensor,
    y_pred: tf.Tensor,
    model: tf.keras.Model = None,
    loss_type: str = "kld",
    temperature: float = 1.0,
) -> tf.Tensor:
    """
    Loss function used for Model Distillation.

    Parameters
    ----------
    x_true
        Batch of data points.
    y_pred
        Batch of prediction from the distilled model.
    model
        tf.keras model.
    loss_type
        Type of loss for distillation. Supported 'kld', 'xent.
    temperature
        Temperature used for model prediction scaling.
        Temperature <1 sharpens the prediction probability distribution.

    Returns
    -------
    Loss value.
    """
    y_true = model(x_true)
    # apply temperature scaling
    if temperature != 1.0:
        y_true = y_true ** (1 / temperature)
        y_true = y_true / tf.reshape(tf.reduce_sum(y_true, axis=-1), (-1, 1))

    if loss_type == "kld":
        loss_dist = kld(y_true, y_pred)
    elif loss_type == "xent":
        loss_dist = categorical_crossentropy(y_true, y_pred, from_logits=False)
    else:
        raise NotImplementedError

    # compute K-L divergence loss
    loss = tf.reduce_mean(loss_dist)

    return loss
