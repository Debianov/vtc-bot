from typing import Any

import discord.ext.test as dpytest
import pytest
from discord.ext import commands

from bot.converters import Expression, SearchExpression, ShortSearchExpression
from bot.data import UserGroup
from bot.exceptions import SearchExpressionNotFound
from bot.utils import DiscordObjEvaluator, MockLocator, removeNesting