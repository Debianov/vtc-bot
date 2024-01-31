import discord

from bot.utils import (Case, DelayedExpression, PartMessageInList,
                       PartMessageInDict, PartFormat, default_format)
from typing import Any, Union


def getDiscordMemberObject(arg: Any) -> Union[str, Any]:
    if isinstance(arg, discord.Member):
        return str(arg.id)
    return arg

current_format = PartFormat(getDiscordMemberObject)

default_case = Case(
    target=PartMessageInList(current_format,
                             DelayedExpression('mockLocator.members[0]')),
    act="23",
    d_in=PartMessageInList(current_format,
                           DelayedExpression('mockLocator.members[1]')),
    flags=PartMessageInDict(default_format, {"-name": "Test", "-output": "",
                             "-priority": "-1", "other": ""})
)

default_case_with_several_users = Case(
    target=PartMessageInList(current_format,
                             DelayedExpression('mockLocator.members[0]'),
                             DelayedExpression('mockLocator.members[1]')),
    act="23",
    d_in=PartMessageInList(current_format,
                           DelayedExpression('mockLocator.members[2]'),
                           DelayedExpression('mockLocator.members[3]')),
    flags=PartMessageInDict(default_format,
        {"-name": "Test", "-output": "", "-priority": "-1",
         "other": ""})
)

default_case_with_other_target_name = Case(
    target=PartMessageInList(current_format,
                             DelayedExpression('mockLocator.members[0]')),
    act="23",
    d_in=PartMessageInList(current_format,
                           DelayedExpression('mockLocator.members[1]')),
    flags=PartMessageInDict(default_format, {"-name": "Aboba", "-output": "",
                             "-priority": "-1",
                             "other": ""})
)