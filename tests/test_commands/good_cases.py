import discord

from bot.utils import (Case, DelayedExpression, ListPartMessage,
                       DictPartMessage, ElemFormater, default_format)
from typing import Any, Union


def getDiscordMemberObject(arg: Any) -> Union[str, Any]:
    if isinstance(arg, discord.Member):
        return str(arg.id)
    return arg

format_for_getting_ds_id = ElemFormater(getDiscordMemberObject)

default_case = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]')),
    act="23",
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[1]')),
    flags=DictPartMessage(default_format, {"-name": "Test",
        "-output": "", "-priority": "-1", "other": ""})
)

default_case_with_several_users = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]'),
                           DelayedExpression('mockLocator.members[1]')),
    act="23",
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[2]'),
                         DelayedExpression('mockLocator.members[3]')),
    flags=DictPartMessage(default_format,
                          {"-name": "Test", "-output": "", "-priority": "-1",
         "other": ""})
)

default_case_with_other_target_name = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]')),
    act="23",
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[1]')),
    flags=DictPartMessage(default_format, {"-name": "Aboba",
        "-output": "", "-priority": "-1", "other": ""})
)

