import sys
import pathlib
import pytest
from typing import Final, Union, Iterable, Optional, Callable, Type

root = pathlib.Path.cwd()

sys.path.append(str(root))
sys.path.append(str(root) + "/bot")

pytest_plugins = ('pytest_asyncio',)

from bot.objects.user_objects import Guild
class ResponsesToTestMessagesStorage(list):
	
	def append(self, element: str) -> None:
		super().append(element)

	def get_first_str(self) -> str:
		try:
			result = super().pop(0)
		except IndexError:
			return ""
		return result if isinstance(result, str) else ""

class MockMember:
	pass

class MockChannel:

	async def send(
		self,
		content: Optional[str] = None,
	) -> None:
		pytest.response_to_test_messages.append(content)

class MockMessage:

	def __init__(
		self,
		channel: MockChannel,
		data: str
	) -> None:
		self.channel = channel
		self.content = data

	def __getattr__(self, attr) -> str:
		return ""

def pytest_configure():
	pytest.global_prefix: Final = "sudo"
	pytest.access_prefix: Final = ""
	pytest.MockMember: Type[MockMember] = MockMember
	pytest.MockChannel: Type[MockChannel] = MockChannel
	pytest.MockMessage: Type[MockMessage] = MockMessage
	pytest.response_to_test_messages: ResponsesToTestMessagesStorage = ResponsesToTestMessagesStorage()

@pytest.fixture(scope="session")
def getGoodGuildInstance() -> Guild:
	return Guild(pytest.global_prefix, pytest.access_prefix)