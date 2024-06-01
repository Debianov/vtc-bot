import discord

from bot.utils import (Case, DelayedExpression, ListPartMessage,
                       ElemFormater, StringPartMessage, DictPartMessage,
                       default_format)

from typing import Any, Union

def getDiscordMemberObject(arg: Any) -> Union[str, Any]:
    if isinstance(arg, discord.Member):
        return str(arg.id)
    return arg

format_for_getting_ds_id = ElemFormater(getDiscordMemberObject)

case_for_coincidence = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]')),
    act=StringPartMessage("26"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[1]')),
    flags=DictPartMessage(default_format, {"-name": "Aboba"})
)

case_for_coincidence_2_1 = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]')),
    act=StringPartMessage("26"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[1]')),
    flags=DictPartMessage(default_format, {"-name": "Aboba"})
)

case_for_coincidence_2_2 = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[2]')),
    act=StringPartMessage("26"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[1]')),
    flags=DictPartMessage(default_format, {"-name": "Aboba"})
)

case_for_coincidence_3_1 = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]'),
                           DelayedExpression('mockLocator.members[1]')),
    act=StringPartMessage("26"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[2]'),
                         DelayedExpression('mockLocator.members[3]')),
    flags=DictPartMessage(default_format, {"-name": "Aboba"})
)

case_for_coincidence_3_2 = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]'),
                           DelayedExpression('mockLocator.members[1]')),
    act=StringPartMessage("26"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[2]')),
    flags=DictPartMessage(default_format, {"-name": "Aboba"})
)


case_for_coincidence_4_1 = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]')),
    act=StringPartMessage("26"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[1]')),
    flags=DictPartMessage(default_format, {"-name": "Aboba"})
)

case_for_coincidence_4_2 = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[2]')),
    act=StringPartMessage("8"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[3]')),
    flags=DictPartMessage(default_format, {"-name": "Aboba"})
)

case_for_coincidence_5_1 = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]')),
    act=StringPartMessage("26"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[1]')),
    flags=DictPartMessage(default_format, {"-name": "Aboba"})
)

case_for_coincidence_5_2 = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]')),
    act=StringPartMessage("26"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[1]')),
    flags=DictPartMessage(default_format, {"-name": "aboba"})
)

case_for_coincidence_6_1 = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]')),
    act=StringPartMessage("26"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[1]')),
    flags=DictPartMessage(default_format, {"-name": "Aboba"})
)

case_for_coincidence_6_2 = Case(
    target=ListPartMessage(format_for_getting_ds_id,
                           DelayedExpression('mockLocator.members[0]')),
    act=StringPartMessage("26"),
    d_in=ListPartMessage(format_for_getting_ds_id,
                         DelayedExpression('mockLocator.members[1]')),
    flags=DictPartMessage(default_format, {"-name": ""})
)