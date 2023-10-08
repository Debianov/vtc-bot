import pathlib
import sys
from typing import Generator
import pytest
import asyncio

root = pathlib.Path.cwd()

sys.path.append(str(root))

pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="package")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
	loop = asyncio.get_event_loop()
	yield loop
	loop.close()