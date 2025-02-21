from aries_askar import Store
import hashlib
import json
import logging
from settings import Settings

logger = logging.getLogger(__name__)


class AskarStorage:
    def __init__(self):
        self.db = Settings.REPORTS_DB
        self.key = Store.generate_raw_key(
            hashlib.md5(Settings.WITNESS_SEED.encode()).hexdigest()
        )

    async def provision(self, recreate=False):
        logger.warning(self.db)
        await Store.provision(self.db, "raw", self.key, recreate=recreate)

    async def open(self):
        return await Store.open(self.db, "raw", self.key)

    async def fetch(self, category, data_key):
        store = await self.open()
        try:
            async with store.session() as session:
                entry = await session.fetch(category, data_key)
            return json.loads(entry.value)
        except:
            return None

    async def store(self, category, data_key, data, tags=None):
        store = await self.open()
        try:
            async with store.session() as session:
                await session.insert(
                    category,
                    data_key,
                    json.dumps(data),
                    tags,
                )
        except:
            return False

    async def update(self, category, data_key, data, tags=None):
        store = await self.open()
        try:
            async with store.session() as session:
                await session.replace(
                    category,
                    data_key,
                    json.dumps(data),
                    tags,
                )
        except:
            return False
