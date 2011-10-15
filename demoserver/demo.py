#!/usr/bin/env python

import web
import json
import string
import random

urls = (
    '/computes/', 'ComputeList',
    '/computes/(\d+)', 'Compute',
    '/networks/', 'NetworkList',
    '/networks/(\d+)', 'Network',
    '/storages/', 'StorageList',
    '/storages/(\d+)', 'Storage',
    '/templates/', 'TemplateList',
    '/templates/(\d+)', 'Template',
    '/news/', 'NewsList',
    '/news/(\d+)', 'News'
)
app = web.application(urls, globals())

def gen_compute_data(id):
    return {'id': id,
            'name': 'hostname %s' %id, 
            'arch': ['x86', 'x64', 'win32', 'win64', 'macosx'][id % 5], 
            'memory': 2*id,
            'cpu': 0.2 * id,
            'cores': range(1,16)[id % 15],
            'template': ['centos5', 'centos6', 'rhel6-jbos', 'winserver2008', 'jetty-cluster'][id % 5],
            'state': ['running', 'stopped', 'suspended'][id % 3]}

def gen_network_data(id):
    return {'id': id,
            'name': 'network %s' %id, 
            'ip': '%s.%s.%s.%s' %(id, id, id, id),
            'mask': '%s.%s.%s.0' %(id * 2, id * 2, id * 2),
            'address_allocation': ['dhcp', 'static'][id % 2], 
            'gateway': '%s.%s.%s.1' %(id * 2, id * 2, id * 2)
           }

def gen_storage_data(id):
    return {'id': id,
            'name': 'network %s' %id, 
            'size': id * 3000,
            'type': ['local', 'iscsi', 'lvm', 'nfs'][id % 4]
            }

def gen_template_data(id):
    return {'id': id,
            'name': ['centos5', 'centos6', 'rhel6-jbos', 'winserver2008', 'jetty-cluster'][id % 5], 
            'min_disk_size': id * 3000,
            'min_memory_size': id * 300
            }

def gen_news_data(id):
    def get_string(length):
        return ''.join(random.choice(string.letters) for i in xrange(length))
    return {'id': id,
            'type': ['info', 'warning', 'error', 'system_message'][id % 4],
            'name': get_string(20),
            'content': get_string(400)
            }

limit = 20

computes = [gen_compute_data(i) for i in range(limit)]
storages = [gen_storage_data(i) for i in range(limit)]
networks = [gen_network_data(i) for i in range(limit)]
templates = [gen_template_data(i) for i in range(limit)]
news = [gen_news_data(i) for i in range(limit)]



class GenericContainer(object):

    resource = {'ComputeList': computes,
                'StorageList': storages,
                'NetworkList': networks,
                'TemplateList': templates,
                'NewsList': news
                }

    def GET(self):
        # deduce resource type from the object name
        cls = self.__class__.__name__
        type = self.resource[cls]

        return json.dumps([{t['id']: t['name']} for t in type])

    def POST(self):
        # deduce resource type from the object name
        cls = self.__class__.__name__
        type = self.resource[cls]

        # create a new object of a given type
        new_id = max([t['id'] for t in type]) + 1
        submitted_data = json.loads(web.data())
        submitted_data.update({'id': new_id})
        type.append(submitted_data)
        return json.dumps(type[-1], sort_keys = 4, indent = 4)

class GenericResource(object):
    
    resource = {'Compute': computes,
                'Storage': storages,
                'Network': networks,
                'Template': templates,
                'News': news
                }

    def PUT(self, id):
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

    def DELETE(self, id):
        id = int(id)
        # deduce resource type from the object name
        cls = self.__class__.__name__
        type = self.resource[cls]

        # locate the object for deleting
        for o in type:
            if o['id'] == id:
                type.remove(o)
                return
        # nothing found
        raise web.notfound()

    def GET(self, id):
        id = int(id)
        cls = self.__class__.__name__
        type = self.resource[cls]

        # locate the object for updating
        for o in type:
            if o['id'] == id:
                return json.dumps(o, sort_keys = 4, indent = 4)
        # nothing found
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


if __name__ == "__main__":
    app.run()
