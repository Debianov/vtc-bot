"""
Модуль предназначен для абстрактных классов.
"""

from typing import Protocol


class IDSupportObjects(Protocol):
	
	id: int
