# -*- coding: utf-8 -*-

from aiohttp import web
from backend import response


class CookbooksView(web.View):
    async def get(self):
        cookbook_mgr = self.request.app['cookbook_mgr']
        cookbooks = await cookbook_mgr.list_cookbook()
        return await response.response(200, 'List cookbook successfully',
                                       cookbooks)

    async def post(self):
        cookbook_mgr = self.request.app['cookbook_mgr']
        cookbook = await self.request.json()
        cookbook_id = await cookbook_mgr.insert_cookbook(cookbook)
        return await response.response(200, 'Create cookbook successfully',
                                       {"id": cookbook_id})


class CookbookView(web.View):
    async def get(self):
        cookbook_mgr = self.request.app['cookbook_mgr']
        cookbook_id = self.request.match_info['id']
        cookbook = await cookbook_mgr.get_cookbook(cookbook_id)
        return await response.response(200, 'Get cookbook successfully',
                                       cookbook)

    async def put(self):
        cookbook_mgr = self.request.app['cookbook_mgr']
        cookbook_id = self.request.match_info['id']
        cookbook = await self.request.json()
        await cookbook_mgr.update_cookbook(cookbook_id, cookbook)
        return await response.response(200, 'Update cookbook successfully',
                                       None)

    async def delete(self):
        cookbook_mgr = self.request.app['cookbook_mgr']
        cookbook_id = self.request.match_info['id']
        await cookbook_mgr.delete_cookbook(cookbook_id)
        return await response.response(200, 'Delete cookbook successfully',
                                       None)
