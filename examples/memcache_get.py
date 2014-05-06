# vim:ts=4:sw=4:expandtab
'''Non blocking memcache get/set.
'''
from diesel import Application, Service, send
from diesel.protocols.memcache import MemcacheClient

def delay_echo_server(addr):
    # default to 127.0.0.1:11211
    m = MemcacheClient('localhost')
    value = m.get('mykey')
    send("value from memcache key : %s %s"%(str(value), str(non_value)))

app = Application()
app.add_service(Service(delay_echo_server, 8013))
app.run()
