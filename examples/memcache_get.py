# vim:ts=4:sw=4:expandtab
'''Non blocking memcache get/set.
'''
from diesel import Application, Service
from diesel.protocols.memcache import MemCacheClient
from diesel.protocols import http
from diesel import log

def delay_echo_server(addr):
    # default to 127.0.0.1:11211
    m = MemCacheClient('localhost')
    value = m.get('mykey')
    values = m.get_multi(['mykey', 'mykey1', 'mykey2'])
    
    return http.Response("value from multi_get : %s and get : %s"%(str(values), str(value)))
    #return http.Response("value from memcache key : %s key1 : %s and key 2 : %s"%(str(value), str(value1), str(value2)))

app = Application()
app.add_service(Service(http.HttpServer(delay_echo_server), 8003))
app.run()
