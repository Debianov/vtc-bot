from bot.utils import Case, DelayedExpression

default_case = Case(
    target=[DelayedExpression('mockLocator.members[0]')],
    act="23",
    d_in=[DelayedExpression('mockLocator.members[1]')],
    flags={"-name": "Test", "-output": "", "-priority": "-1", "other": ""}
)

default_case_with_several_users = Case(
    target=[DelayedExpression('mockLocator.members[0]'), DelayedExpression('mockLocator.members[1]')],
    act="23",
    d_in=[DelayedExpression('mockLocator.members[2]'), DelayedExpression('mockLocator.members[3]')],
    flags={"-name": "Test", "-output": "", "-priority": "-1", "other": ""}
)

default_case_with_other_target_name = Case(
    target=[DelayedExpression('mockLocator.members[0]')],
    act="23",
    d_in=[DelayedExpression('mockLocator.members[1]')],
    flags={"-name": "Aboba", "-output": "", "-priority": "-1", "other": ""}
)