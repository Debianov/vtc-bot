from bot.utils import DelayedExpression, Language

guild_description_attrs = [
    435,
    Language(short_name="en")
]
guild_desc_instance_changed_attrs = {"selected_language":
                                    Language(short_name="ru")}

log_target_attrs = [
    2,
    [DelayedExpression("mockLocator.members[0]")],
    5,
    [DelayedExpression("mockLocator.members[1]")],
    "sdq"
]
log_target_instance_changed_attrs = {"target":
    [DelayedExpression("mockLocator.members[2]")]}