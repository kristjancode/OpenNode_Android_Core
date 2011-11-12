#!/usr/bin/env python

import web
import json
import string
import random
import datetime
import basicauth


urls = (
    '/', 'AllResourcesList', 
    '/computes/', 'ComputeList',
    '/computes/(\d+)/', 'Compute',
    '/networks/', 'NetworkList',
    '/networks/(\d+)/', 'Network',
    '/storages/', 'StorageList',
    '/storages/(\d+)/', 'Storage',
    '/templates/', 'TemplateList',
    '/templates/(\d+)/', 'Template',
    '/news/', 'NewsList',
    '/news/(\d+)/', 'News',
    '/news/(\d+)/comments/', 'CommentList'
    )

app = web.application(urls, globals())

def gen_compute_data(id):
    return {'id': id,
            'name': 'hostname_%s' %id, 
            'arch': ['x86', 'x64', 'win32', 'win64', 'macosx'][id % 5], 
            'memory': 2*id,
            'cpu': 0.2 * id,
            'cores': range(1,16)[id % 15],
            'template': ['centos5', 'centos6', 'rhel6-jbos', 'winserver2008', 'jetty-cluster'][id % 5],
            'state': ['running', 'stopped', 'suspended'][id % 3]}

def gen_network_data(id):
    return {'id': id,
            'name': 'network_%s' %id, 
            'ip': '%s.%s.%s.%s' %(id, id, id, id),
            'mask': '%s.%s.%s.0' %(id * 2, id * 2, id * 2),
            'address_allocation': ['dhcp', 'static'][id % 2], 
            'gateway': '%s.%s.%s.1' %(id * 2, id * 2, id * 2)
           }

def gen_storage_data(id):
    mult = random.randint(1, 3000)
    return {'id': id,
            'name': 'storage_pool_%s' %id, 
            'capacity': id * 3000,
            'available': id*mult,
            'type': ['local', 'iscsi', 'lvm', 'nfs'][id % 4]
            }

def gen_template_data(id):
    return {'id': id,
            'name': ['centos5', 'centos6', 'rhel6-jboss', 'winserver2008', 'jetty-cluster'][id % 5], 
            'min_disk_size': id * 3000,
            'min_memory_size': id * 300,
            'min_cpu': 2,
            'max_cpu': 4,
            'max_disk_size': id * 2000000,
            'max_memory_size': id * 200000,
            }

def gen_news_data(id):
    def get_string(length):
        return ''.join(random.choice(string.ascii_letters) for i in xrange(length))
    return {'id': id,
            'type': ['info', 'warning', 'error', 'system_message'][id % 4],
            'name': 'Wow!: ' + get_string(20),
            'content': get_string(400),
            'comments': [{idc: (datetime.datetime.now().isoformat(), ['andres', 'ilja', 'erik', 'marko', 'sasha'][idc % 5], 
                'I think that ' + get_string(10))} for idc in range(1,10)],
            }

limit = 20

computes = [gen_compute_data(i) for i in range(limit)]
storages = [gen_storage_data(i) for i in range(limit)]
networks = [gen_network_data(i) for i in range(limit)]
templates = [gen_template_data(i) for i in range(limit)]
news = [gen_news_data(i) for i in range(limit)]

allresources = computes + storages + networks + templates + news

def myVerifier(username, password, realm):
    return username == "opennode" and password == "demo"

auth = basicauth.auth(verify = myVerifier)

class GenericContainer(object):

    resource = {'ComputeList': computes,
                'StorageList': storages,
                'NetworkList': networks,
                'TemplateList': templates,
                'NewsList': news,
                'AllResourcesList': allresources
                }
    
    def OPTIONS(self):
        web.header('Access-Control-Allow-Methods', web.ctx.environ['HTTP_ACCESS_CONTROL_REQUEST_METHOD'])
        web.header('Access-Control-Allow-Headers', web.ctx.environ['HTTP_ACCESS_CONTROL_REQUEST_HEADERS'])
        web.header('Access-Control-Allow-Origin', web.ctx.environ['HTTP_ORIGIN'])

    @auth
    def GET(self):
        if 'HTTP_ORIGIN' in web.ctx.environ:
            web.header('Access-Control-Allow-Origin', web.ctx.environ['HTTP_ORIGIN'])
        
        # extract search parameters
        def filter(o):
            """Evaluate whether object matches request query"""
            q = web.ctx.query
            if q.rfind('q=') == -1:
                return True
            else:
                terms = q[q.index('q=') + 2:].decode('utf8').split('&')
                # iterate over search terms, return True for the first hit
                for t in terms:
                    if o['name'].rfind(t) != -1:
                        return True
            return False
        # deduce resource type from the object name
        cls = self.__class__.__name__
        type = self.resource[cls]

        return json.dumps([t for t in type if filter(t)], indent = 4)

    def _publish_news(self, item_type, item_text):
        new_id = max([t['id'] for t in news]) + 1
        news_item['id'] = new_id
        news_item['name'] = "New object: %s" %item_type
        news_item['type'] = 'info'
        news_item['content'] = "%s: %s" % (datetime.datetime.now().isoformat(),text, item_text)
        news.append(new_item)
        allresources.append(news_item)

    @auth
    def POST(self):
        if 'HTTP_ORIGIN' in web.ctx.environ:
            web.header('Access-Control-Allow-Origin', web.ctx.environ['HTTP_ORIGIN'])

        # deduce resource type from the object name
        cls = self.__class__.__name__
        type = self.resource[cls]

        # create a new object of a given type
        new_id = max([t['id'] for t in type]) + 1
        submitted_data = json.loads(web.data())
        submitted_data.update({'id': new_id})
        type.append(submitted_data)
        allresources.append(submitted_data)
#        self._publish_news(cls, 'Create a new object of type %s ith id %' % (type, new_id))
        return json.dumps(type[-1], sort_keys = 4, indent = 4)

    
class GenericResource(object):
    
    resource = {'Compute': computes,
                'Storage': storages,
                'Network': networks,
                'Template': templates,
                'News': news
                }

    def OPTIONS(self, id):
        web.header('Access-Control-Allow-Methods', web.ctx.environ['HTTP_ACCESS_CONTROL_REQUEST_METHOD'])
        web.header('Access-Control-Allow-Headers', web.ctx.environ['HTTP_ACCESS_CONTROL_REQUEST_HEADERS'])
        web.header('Access-Control-Allow-Origin', web.ctx.environ['HTTP_ORIGIN'])

    @auth
    def PUT(self, id):
        if 'HTTP_ORIGIN' in web.ctx.environ:
            web.header('Access-Control-Allow-Origin', web.ctx.environ['HTTP_ORIGIN'])

        id = int(id)
        # deduce resource type from the object name
        cls = self.__class__.__name__
        type = self.resource[cls]

        # locate the object for updating
        for o in type:
            if o['id'] == id:
                submitted_data = json.loads(web.data())
                o.update(submitted_data)
                o['id'] = id # just in case request overwrites it
                return json.dumps(o, sort_keys = 4, indent = 4)
        # nothing found
        raise web.notfound()

    @auth
    def DELETE(self, id):
        if 'HTTP_ORIGIN' in web.ctx.environ:
            web.header('Access-Control-Allow-Origin', web.ctx.environ['HTTP_ORIGIN'])
        id = int(id)
        # deduce resource type from the object name
        cls = self.__class__.__name__
        type = self.resource[cls]

        # locate the object for deleting
        for o in type:
            if o['id'] == id:
                type.remove(o)
                allresources.remove(o)
                return
        # nothing found
        raise web.notfound()

    @auth
    def GET(self, id):
        if 'HTTP_ORIGIN' in web.ctx.environ:
            web.header('Access-Control-Allow-Origin', web.ctx.environ['HTTP_ORIGIN'])
        id = int(id)
        cls = self.__class__.__name__
        resource_type = self.resource[cls]
        # locate object
        for obj in resource_type:
            if obj['id'] == id:
                return json.dumps(obj, sort_keys = 4, indent = 4)
        raise web.notfound()


class ComputeList(GenericContainer): pass
class Compute(GenericResource): pass

class NetworkList(GenericContainer): pass
class Network(GenericResource): pass

class StorageList(GenericContainer): pass
class Storage(GenericResource): pass

class TemplateList(GenericContainer): pass
class Template(GenericResource): pass

class NewsList(GenericContainer): pass
class News(GenericResource): pass

class AllResourcesList(GenericContainer): pass

class CommentList(object):
    
    @auth
    def POST(self, newsid):
        print newsid
        if 'HTTP_ORIGIN' in web.ctx.environ:
            web.header('Access-Control-Allow-Origin', web.ctx.environ['HTTP_ORIGIN'])

        # load corresponding news
        foundNews = None
        for n in news:
            if int(n['id']) == int(newsid):
                foundNews = n
                break

        if foundNews is None:
            raise web.notfound()

        # append a new comment to the news
        new_id = max(foundNews['comments']).keys()[0] + 1
        submitted_data = json.loads(web.data())
        foundNews['comments'].append({new_id: (datetime.datetime.now().isoformat(), 
                            submitted_data['author'], submitted_data['content'])})
        return json.dumps(foundNews, sort_keys = 4, indent = 4)

if __name__ == "__main__":
    app.run()
