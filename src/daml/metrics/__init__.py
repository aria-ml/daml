from daml._internal.deps import is_alibi_detect_available

from . import ber, divergence

__all__ = ["ber", "divergence"]

if is_alibi_detect_available():  # pragma: no cover
    from . import outlier_detection  # noqa F401

    __all__ += ["outlier_detection"]

del is_alibi_detect_available
