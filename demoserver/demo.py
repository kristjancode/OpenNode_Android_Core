#!/usr/bin/env python

import web
import json
import string
import random

urls = (
    '/computes', 'ComputeList',
    '/computes/(\d+)', 'Compute',
    '/networks', 'NetworkList',
    '/networks/(\d+)', 'Network',
    '/storages', 'StorageList',
    '/storages/(\d+)', 'Storage',
    '/templates', 'TemplateList',
    '/templates/(\d+)', 'Template',
    '/news', 'NewsList',
    '/news/(\d+)', 'News'
)
app = web.application(urls, globals())

def gen_compute_data(id):
    id = int(id)
    return {'id': id,
            'hostname': 'hostname %s' %id, 
            'arch': ['x86', 'x64', 'win32', 'win64', 'macosx'][id % 5], 
            'memory': 2*id,
            'cpu': 0.2 * id,
            'cores': range(1,16)[id % 15],
            'template': ['centos5', 'centos6', 'rhel6-jbos', 'winserver2008', 'jetty-cluster'][id % 5],
            'state': ['running', 'stopped', 'suspended'][id % 3]}

def gen_network_data(id):
    id = int(id)
    return {'id': id,
            'name': 'network %s' %id, 
            'ip': '%s.%s.%s.%s' %(id, id, id, id),
            'mask': '%s.%s.%s.0' %(id * 2, id * 2, id * 2),
            'address_allocation': ['dhcp', 'static'][id % 2], 
            'gateway': '%s.%s.%s.1' %(id * 2, id * 2, id * 2)
           }

def gen_storage_data(id):
    id = int(id)
    return {'id': id,
            'name': 'network %s' %id, 
            'size': id * 3000,
            'type': ['local', 'iscsi', 'lvm', 'nfs'][id % 4]
            }

def gen_template_data(id):
    id = int(id)
    return {'id': id,
            'name': 'network %s' %id, 
            'min_disk_size': id * 3000,
            'min_memory_size': id * 300
            }

def gen_news_data(id):
    id = int(id)
    def get_string(length):
        return ''.join(random.choice(string.letters) for i in xrange(length))
    return {'id': id,
            'type': ['info', 'warning', 'error', 'system_message'][id % 4],
            'title': get_string(20),
            'content': get_string(400)
            }


class ComputeList(object):
    def GET(self):
        limit = 20
        return json.dumps([{x: gen_compute_data(x)['hostname']} for x in range(limit)])

class Compute(object):
    def GET(self, id):
        return json.dumps(gen_compute_data(id), sort_keys = 4, indent = 4)

class NetworkList(object):
    def GET(self):
        limit = 20
        return json.dumps([{x: gen_network_data(x)['name']} for x in range(limit)])

class Network(object):
    def GET(self, id):
        return json.dumps(gen_network_data(id), sort_keys = 4, indent = 4)

class StorageList(object):
    def GET(self):
        limit = 20
        return json.dumps([{x: gen_storage_data(x)['name']} for x in range(limit)])

class Storage(object):
    def GET(self, id):
        return json.dumps(gen_storage_data(id), sort_keys = 4, indent = 4)

class TemplateList(object):
    def GET(self):
        limit = 20
        return json.dumps([{x: gen_template_data(x)['name']} for x in range(limit)])

class Template(object):
    def GET(self, id):
        return json.dumps(gen_template_data(id), sort_keys = 4, indent = 4)

class NewsList(object):
    def GET(self):
        limit = 20
        return json.dumps([{x: gen_news_data(x)['title']} for x in range(limit)])

class News(object):
    def GET(self, id):
        return json.dumps(gen_news_data(id), sort_keys = 4, indent = 4)


if __name__ == "__main__":
    app.run()