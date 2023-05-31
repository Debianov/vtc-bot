import discord
import pytest
import pytest_asyncio
import psycopg
from typing import Optional, Any

from bot.main import initDB

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="package", name="db")
async def setupDB() -> Optional[psycopg.AsyncConnection[Any]]:
	with open("test_db_secret.sec") as text:
		aconn = await initDB(text.readline(), text.readline())
		return aconn

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="package", autouse=True)
async def createTargetTable(db) -> None:
	async with db.cursor() as acur:
		await acur.execute(
			"""CREATE TABLE public.target (
			id bigint,
			context_id bigint,
			target bigint[],
			act text,
			d_in bigint[],
			name text,
			priority integer,
			output text,
			other text
			);"""
		)
		yield
		await acur.execute(
			"""
			DROP TABLE target;
			"""
		)

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="function", autouse=True)
async def deleteTargetTable(db) -> None:
	yield
	async with db.cursor() as acur:
		await acur.execute(
			"DELETE FROM target;"
		)