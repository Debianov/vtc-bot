from typing import Any, Dict

import psycopg
import pytest
from .all_db_objects_group_subs import (
	guild_desc_instance_changed_attrs,
	guild_description_instance,
	log_target_instance,
	log_target_instance_changed_attrs
)

from bot.data import (
	DBObjectGroup,
	GuildDescription,
	GuildDescriptionFabric,
	convertToListMap,
	createDBRecord,
	findFromDB,
	updateDBRecord
)
from bot.exceptions import DuplicateInstanceError
from bot.utils import Language


@pytest.mark.parametrize(
    "instance, changed_attrs",
    (
        [guild_description_instance, guild_desc_instance_changed_attrs],
        [log_target_instance, log_target_instance_changed_attrs]
    )
)
@pytest.mark.asyncio
async def test_writingToDB(
        dbconn: psycopg.AsyncConnection[Any],
        instance: DBObjectGroup,
        changed_attrs: Dict[str, Any]
):
    await createDBRecord(dbconn, instance)
    instance.record_id = 0
    for key, value in changed_attrs:
        setattr(instance, key, value)
    await updateDBRecord(dbconn, instance)
    instances = await findFromDB(dbconn, instance.__class__, record_id=0)
    assert instances[0] == instance
    assert len(instances) <= 1, DuplicateInstanceError

@pytest.mark.parametrize(
    "instance, changed_attrs",
    (
        [guild_description_instance, guild_desc_instance_changed_attrs],
        [log_target_instance, log_target_instance_changed_attrs]
    )
)
@pytest.mark.asyncio
async def test_createDBRecordAsUpdate(
        dbconn: psycopg.AsyncConnection[Any],
        instance: DBObjectGroup,
        changed_attrs: Dict[str, Any]
):
    await createDBRecord(dbconn, instance)
    instance.record_id = 0
    changed_instance = instance
    for key, value in changed_attrs:
        setattr(changed_instance, key, value)
    await createDBRecord(dbconn, changed_instance)
    instances = await findFromDB(dbconn, instance.__class__, record_id=0)
    assert instances[0] == instance
    assert instances[1] == changed_instance
    assert len(instances) <= 2
