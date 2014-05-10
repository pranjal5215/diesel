# vim:ts=4:sw=4:expandtab
'''Non blocking memcache get/set.
'''
from diesel import Application, Service
from diesel.protocols.memcache import MemCacheClient
from diesel.protocols import http

def delay_echo_server(addr):
    # default to 127.0.0.1:11211
    m = MemCacheClient('localhost')
    value = m.get('mykey')
    return http.Response("value from memcache key : %s"%str(value))

app = Application()
app.add_service(Service(http.HttpServer(delay_echo_server), 8003))
app.run()
