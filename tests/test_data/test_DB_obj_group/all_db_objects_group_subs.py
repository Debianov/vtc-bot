from bot.data import GuildDescriptionFabric, LogTargetFabric
from bot.mock import IDHolder
from bot.utils import Language

guild_description_instance = GuildDescriptionFabric("435", Language("english"))
guild_desc_instance_changed_attrs = {"guild_id": "4536456"}

log_target_instance = LogTargetFabric(2, [IDHolder(2345)], ["5"],
[IDHolder(57567)],"sdq")
log_target_instance_changed_attrs = {"target": IDHolder(768)}

