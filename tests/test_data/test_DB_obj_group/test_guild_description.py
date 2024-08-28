import pytest

from bot.data import GuildDescriptionFactory
from bot.utils import Language


def test_GildDescriptionFabric():
    instance = GuildDescriptionFactory(2, Language("ru")).getInstance()

def test_GuildDescriptionChangeMap():
    instance = GuildDescriptionFactory(2, Language("ru")).getInstance()
    instance.guild_id = 4
    assert instance._change_map == {'guild_id': True}

def test_GuildDescriptionIteration():
    instance = GuildDescriptionFactory(2, Language("ru")).getInstance()
    instance.guild_id = 4
    for status, (field, _) in instance:
        if field == "guild_id":
            assert status is True
        else:
            assert status is False