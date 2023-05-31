import pytest
import discord.ext.test as dpytest

@pytest.mark.asyncio
async def test_main_help_page() -> None:
	await dpytest.message("sudo help")
	assert dpytest.verify().message()