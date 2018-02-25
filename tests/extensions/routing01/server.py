from tozti.utils import RouterDef
from aiohttp import web


router = RouterDef()
foo = router.add_route('/foo')


@foo.get
async def foo_get(req):
    return web.Response(
        text='foo')


MANIFEST = {
    'name': 'routing01',
    'router': router,
}
