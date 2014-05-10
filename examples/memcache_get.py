# vim:ts=4:sw=4:expandtab
'''Non blocking memcache get/set.
'''
from diesel import Application, Service
from diesel.protocols.memcache import MemCacheClient
from diesel.protocols import http

def mem_get_client(addr):
    # default to 127.0.0.1:11211
    m = MemCacheClient('localhost')
    single_value = m.get('mykey')
    multi_value = m.get_multi(['mykey', 'multikey', 'storedkey'])
    return http.Response("Value from single get : %s\nValue from \
        multi get : %s  "%(str(single_value), str(multi_value)))

app = Application()
app.add_service(Service(http.HttpServer(mem_get_client), 8013))
app.run()
