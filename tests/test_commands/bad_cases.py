import discord

from bot.utils import (Case, DelayedExpression, ListPartMessage,
                       ElemFormater, StringPartMessage, default_format)
from typing import Any, Union


def getDiscordMemberObject(arg: Any) -> Union[str, Any]:
    if isinstance(arg, discord.Member):
        return str(arg.id)
    return arg

format_for_getting_ds_id = ElemFormater(getDiscordMemberObject)

case_without_two_required_params = Case(
    target=ListPartMessage(
        format_for_getting_ds_id,
        DelayedExpression('mockLocator.members[0]')
    ),
    act=StringPartMessage(""),
    d_in=ListPartMessage(default_format, "")
    )


case_without_one_required_params = Case(
    target=ListPartMessage(
        format_for_getting_ds_id,
        DelayedExpression('mockLocator.members[0]')
    ),
    act="23",
    d_in=ListPartMessage(default_format, "")
)

case_without_explicit_flag = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression("mockLocator.members[0]")),
    act="54",
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression("mockLocator.members[1]")),
    flags="barhatniy_tyagi"
)
