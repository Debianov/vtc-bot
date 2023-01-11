import discord # TODO отсутствуют stubs-ы.
# TODO import objects
from objects.user_objects import Guild, UserMessage, Content, DeterminingParameterError

intents = discord.Intents.all()

# TODO проблемка с логами.
# handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')

client = discord.Client(intents=intents)

@client.event
async def on_message(message_instance: discord.Message) -> None:
	guild = Guild("sudo", "")
	content = Content(message_instance.content, message_instance.mentions, message_instance.channel_mentions)
	message = UserMessage(message_instance.id, message_instance.author,
	111, guild, content, message_instance.channel) # TODO timer object.
	if message.isCommand():
		try:
			await message.reply() # TODO мне кажется, стоит разбить reply на handle и reply. Дальше по мере начала реализации бизнес-логики посмотрим.
		except DeterminingParameterError as instance:
			await message.reply_by_custome_text(instance.getErrorText())
	else:
		await message.handle()  # TODO антиспам, антифлуд, логирование и проч., и проч.

with open("secret.sec") as text:
	client.run(text.readline())