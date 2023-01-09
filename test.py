from objects.user_objects import Guild, UserMessage, Content
import asyncio

async def on_message() -> None:
	guild = Guild("sudo", "")
	content = Content("sudo log 1 -name 324234 -target 234234 -act 23424324", 23, 43)
	message = UserMessage(1231242, "ads",
	111, guild, content, "232342342332") # TODO timer object.
	if message.isCommand():
		await message.reply()
	else:
		await message.handle()  # TODO антиспам, антифлуд, логирование и проч., и проч.

asyncio.run(on_message())