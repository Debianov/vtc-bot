from typing import Any, Dict, Type, List
import psycopg
import pytest
from .all_db_objects_group_subs import (
	guild_desc_instance_changed_attrs,
	guild_description_attrs,
	log_target_attrs,
	log_target_instance_changed_attrs
)

from bot.utils import MockLocator
from bot.data import (
	DBObjectsGroupFactory,
	GuildDescriptionFactory,
	LogTargetFactory,
	createDBRecord,
	findFromDB,
	updateDBRecord
)
from bot.exceptions import DuplicateInstanceError


@pytest.mark.parametrize(
	"fabric, attrs_for_instance, changed_attrs",
	(
			[GuildDescriptionFactory, guild_description_attrs, guild_desc_instance_changed_attrs],
			[LogTargetFactory, log_target_attrs, log_target_instance_changed_attrs]
	)
)
@pytest.mark.doDelayedExpression
@pytest.mark.asyncio
async def test_writingToDB(
	db: psycopg.AsyncConnection[Any],
	mockLocator: MockLocator,
	fabric: Type[DBObjectsGroupFactory],
	attrs_for_instance: List[Any],
	changed_attrs: Dict[str, Any]
):
	instance = fabric(*attrs_for_instance).getInstance()
	await createDBRecord(db, instance)
	for key, value in changed_attrs.items():
		setattr(instance, key, value)
	await updateDBRecord(db, instance)
	instances = await findFromDB(db, instance.__class__, guild_id=instance.guild_id)
	finded_instance = instances[0]
	assert len(instances) <= 1, DuplicateInstanceError
	for _, (key, value) in finded_instance:
		value_of_instance = getattr(instance, key)
		assert value_of_instance == value

@pytest.mark.parametrize(
	"fabric, attrs_for_instance, changed_attrs",
	(
			[GuildDescriptionFactory, guild_description_attrs, guild_desc_instance_changed_attrs],
			[LogTargetFactory, log_target_attrs, log_target_instance_changed_attrs]
	)
)
@pytest.mark.doDelayedExpression
@pytest.mark.asyncio
async def test_createDBRecordAsUpdate(
	db: psycopg.AsyncConnection[Any],
	mockLocator: MockLocator,
	fabric: Type[DBObjectsGroupFactory],
	attrs_for_instance: List[Any],
	changed_attrs: Dict[str, Any]
):
	instance = fabric(*attrs_for_instance).getInstance()
	await createDBRecord(db, instance)
	changed_instance = fabric(*attrs_for_instance).getInstance()
	for key, value in changed_attrs.items():
		setattr(changed_instance, key, value)
	await createDBRecord(db, changed_instance)
	instances = await findFromDB(db, instance.__class__, guild_id=instance.guild_id)
	assert instances[0] == instance
	assert instances[1] == changed_instance
	assert len(instances) <= 2
