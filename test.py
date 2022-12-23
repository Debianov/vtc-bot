import asyncio
from command_handler import Guild, UserMessage

guild_inst = Guild("sudo", "")
msg = UserMessage(34, "Aboba", guild_inst, "sudo log 1 56456 323232 243423 342324 432423 432234 24324342 342243", "AS", 3)
async def test():
	await msg.handle()
asyncio.run(test())