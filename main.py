import discord # TODO отсутствуют stubs-ы.
from command_handler import Guild, UserMessage

intents = discord.Intents.all()

# TODO проблемка с логами.
# handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')

client = discord.Client(intents=intents)

@client.event
async def on_message(message_instance: discord.Message) -> None:
	guild_instance = Guild("sudo", "")
	message = UserMessage(message_instance.id, message_instance.author,
	guild_instance, message_instance.content, message_instance.channel, 111)
	# TODO timer object; переопределение __init__ discord.Message
	# TODO (https://translated.turbopages.org/proxy_u/en-ru.ru.747df279-63a06915-
	# TODO dc461e37-74722d776562/https/stackoverflow.com/questions/394770/
	# TODO override-a-method-at-instance-level)
	await message.handle()

with open("secret.sec") as text:
	client.run(text.readline())