import discord # TODO отсутствуют stubs-ы.
from objects.user_objects import Guild, UserMessage, Content
from objects.exceptions import Error
import logging

intents = discord.Intents.all()

discord.utils.setup_logging(level=logging.DEBUG)

client = discord.Client(intents=intents)

@client.event
async def on_message(message_instance: discord.Message) -> None:
	guild = Guild("sudo", "")
	content = Content(message_instance.content, guild.getGlobalPrefix(), guild.getAccessPrefix())
	message = UserMessage(message_instance.id, message_instance.author,
	111, guild, content, message_instance.channel) # TODO timer object.
	if message.isCommand():
		try:
			await message.reply() # TODO мне кажется, стоит разбить reply на handle и
			# TODO reply. Дальше по мере начала реализации бизнес-логики посмотрим.
		except Error as instance:
			await message.reply_by_custome_text(instance.getText())
	else:
		await message.handle()  # TODO антиспам, антифлуд, логирование и проч., и
		# проч.

def run():
	with open("secret.sec") as text:
		client.run(text.readline())