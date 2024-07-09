1. How fix "Skipping analyzing module "example" is installed, but missing library stubs or py.typed marker
import-untyped"

    Make sure that you using relative imports and added __init__.py in a module which contains "example" not founding
    module. That issue relate with the Mypy module lookup `model`_.

.. _model: https://mypy.readthedocs.io/en/stable/running_mypy.html