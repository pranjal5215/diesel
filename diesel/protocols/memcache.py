from diesel import Client, send, receive, until_eol, first, call

MEMCACHE_PORT = 11211

STATUS_MESSAGES = [
    'END',
    'STORED',
    'OK',
    'VALUE',
    'STAT',
    'VERSION',
    'DELETED',
    'TOUCHED',
    ]

ERROR_MESSAGES = [
    'ERROR',
    'CLIENT_ERROR',
    'SERVER_ERROR',
    ]

class MemCacheError(Exception): pass

class MemcacheClient(Client):
    def __init__(self, host='localhost', port=MEMCACHE_PORT, password=None, **kw):
        self.password = password
        Client.__init__(self, host, port, **kw)

    @call
    def get(self, k):
        self._send('get', k)
        resp = self._get_response()
        return resp

    def _send(self, cmd, *args, **kwargs):
        send('%s %s\r\n'%(cmd, args[0]))

    def _handle_value(self, data):
        # data = ['mykey' ,'0', '12']
        data_size = int(data[-1])
        resp = receive(data_size)
        until_eol() # noop
        return resp

    def _get_response(self):
        fl = until_eol().strip()
        resp_list = fl.split(' ')
        status = resp_list[0]
        if status in ERROR_MESSAGES:
            # Error has occured
            e_message = fl[1:]
            raise MemCacheError(e_message)
        elif status in STATUS_MESSAGES:
            if hasattr(self, '_handle_%s'%status.lower()):
                return getattr(self, '_handle_%s'%status.lower())(
                    resp_list[1:])

