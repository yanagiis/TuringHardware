# -*- coding: utf-8 -*-

from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId


class CookbookManager(object):
    def __init__(self, url):
        self._url = url
        self._db_client = None
        self._db = None

    async def connect(self):
        self._db_client = AsyncIOMotorClient(self._url)
        self._db = self._db_client.get_default_database()
        return True

    async def disconnect(self):
        pass

    async def list_cookbook(self):
        collection = self._db.get_collection('cookbook')
        cookbooks = collection.find({})
        return [
            CookbookManager.convert_cookbook(cookbook)
            for cookbook in await cookbooks.to_list(None)
        ]

    async def get_cookbook(self, cookbook_id):
        collection = self._db.get_collection('cookbook')
        cookbook = await collection.find_one({'_id': ObjectId(cookbook_id)})
        return CookbookManager.convert_cookbook(cookbook)

    async def update_cookbook(self, cookbook_id, content):
        collection = self._db.get_collection('cookbook')
        del content['id']
        result = await collection.replace_one({
            '_id': ObjectId(cookbook_id)
        }, content)
        if result.modified_count != 1:
            return False
        return True

    async def delete_cookbook(self, cookbook_id):
        collection = self._db.get_collection('cookbook')
        result = await collection.delete_one({'_id': ObjectId(cookbook_id)})
        if result.deleted_count != 1:
            return False
        return True

    async def insert_cookbook(self, content):
        collection = self._db.get_collection('cookbook')
        result = await collection.insert_one(content)
        return result.inserted_id

    @staticmethod
    def convert_cookbook(cookbook):
        cookbook_id = cookbook['_id']
        del cookbook['_id']
        cookbook['id'] = str(cookbook_id)
        return cookbook


async def main():
    mgr = CookbookManager(
        'mongodb://turingcoffee:turingcoffeepassword@ds021000.mlab.com:21000/turing-coffee'
    )
    await mgr.connect()
    await mgr.insert_cookbook('hello world')
    await mgr.list_cookbook()


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
