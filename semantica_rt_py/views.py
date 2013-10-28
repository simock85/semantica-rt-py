from cornice import Service
from colander import MappingSchema, SchemaNode, String
import facebook
from semantica_rt_py.persistence_config import mongodb


FB_APP_ID = '156235004569304'


class AddPageSchema(MappingSchema):
    user_token = SchemaNode(String(), location='body', type='str')
    page_id = SchemaNode(String(), location='body', type='str')


pages = Service(name='pages', path='/pages', description="Pages service", renderer='bson')


@pages.post(schema=AddPageSchema)
def post_pages(request):
    page_id = request.validated['page_id']
    token = request.validated['user_token']
    graph = facebook.GraphAPI(token)
    try:
        graph.put_object(page_id, 'tabs', app_id=FB_APP_ID)
    except Exception as e:
        request.errors.add(None, 'facebook', e.message)
        return {}
    page_ = mongodb.pages.find_and_modify(query={'page_id': page_id},
                                          update={
                                              '$set': {'page_id': page_id,
                                                       'user_token': token}},
                                          upsert=True)
    return page_


class GetUpdatesSchema(MappingSchema):
    page_id = SchemaNode(String(), location="querystring", type='str', required=False)


updates = Service(name='updates', path='/updates', description='Updates service', renderer='bson')


@updates.get(schema=GetUpdatesSchema)
def get_updates(request):
    q = {'already_sent': 0}
    if request.validated['page_id']:
        q.update({'page_id': request.validated['page_id']})
    mongodb.updates.update(q, {'$set': {'already_sent': 1}}, multi=True)
    updates = mongodb.updates.find(q)
    updates['_id'] = str(updates['_id'])
    return updates

