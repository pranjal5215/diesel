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

class MemCacheClient(Client):
    def __init__(self, host='localhost', port=MEMCACHE_PORT, password=None, **kw):
        self.password = password
        Client.__init__(self, host, port, **kw)

    @call
    def get(self, k):
        send('get %s\r\n'%str(k))
        resp = self._get_response()
        value = None
        if resp:
            key ,value = resp
            # Only if we have received a valid response 
            # for the last key fetch from socket.
            self._get_response()
        return value

    @call
    def get_multi(self, list_keys):
        cmd = 'get'
        for key in list_keys:
            cmd = '%s %s'%(cmd, key)
        cmd = '%s\r\n'%cmd
        send(cmd)
        resp = 1
        resp_dict = {}
        while resp:
            resp = self._get_response()
            if resp:
                key ,value = resp
                resp_dict[key] = value
        return resp_dict

    def _handle_value(self, data):
        '''Handle function status for successful response for get key.
        data_size for the size of response i.e value of the key.
        '''
        key = data[0]
        data_size = int(data[-1])
        value = receive(data_size)
        # After value is received fetch \r\n.
        until_eol()
        return key, value

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
            raise MemCacheError(status)
        elif status in STATUS_MESSAGES:
            if hasattr(self, '_handle_%s'%status.lower()):
                return getattr(self, '_handle_%s'%status.lower())(
                    resp_list[1:])
        else:
            e_message = 'UNKNOWN ERROR'
            raise MemCacheNotFoundError(e_message)

