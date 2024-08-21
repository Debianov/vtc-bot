import pytest

from bot.data import GuildDescription, GuildDescriptionFabric
from bot.utils import Language


def test_GildDescriptionFabric():
    instance = GuildDescriptionFabric(2, Language("ru")).getInstance()
    assert instance.record_id == -1

def test_GuildDescriptionChangeMap():
    instance = GuildDescriptionFabric(2, Language("ru")).getInstance()
    instance.guild_id = 4
    assert instance._change_map == {'guild_id': True}

def test_GuildDescriptionIteration():
    instance = GuildDescriptionFabric(2, Language("ru")).getInstance()
    instance.guild_id = 4
    for status, (field, _) in instance:
        if field == "guild_id":
            assert status is True
        else:
            assert statis is False