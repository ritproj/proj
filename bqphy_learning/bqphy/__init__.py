"""BQPhy Python bindings."""

from importlib import import_module

from ._version import __version__  # noqa: F401

try:
    BQPhy_OPTIMISER = import_module('.BQPhy_Optimiser', __name__).BQPhy_OPTIMISER
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        'The native extension BQPhy_Optimiser is not available. '
        'Build the extension before importing bqphy.'
    ) from exc

__all__ = ['BQPhy_OPTIMISER', '__version__']