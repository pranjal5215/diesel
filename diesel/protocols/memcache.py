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

class MemCacheNotFoundError(Exception): pass

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
        '''Handle function status for successful response for get key.
        data_size for the size of response i.e value of the key.
        '''
        data_size = int(data[-1])
        resp = receive(data_size)
        until_eol() # noop
        return resp

    def _handle_end(self, data):
        return None

    def _get_response(self):
        '''Identifies whether call status from memcache socket protocol 
        response. Always return response calling _handle_`status` function
        '''
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
        else:
            raise MemCacheNotFoundError(e_message)

