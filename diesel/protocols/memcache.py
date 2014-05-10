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
    def get(self, key):
        key_cmd = 'get'
        mem_cmd = '%s %s\r\n'%(key_cmd, key)
        send(mem_cmd)
        # key and corresponding value from memcache
        #resp_value can be None if key not found or k,v tuple
        resp_value = self._get_response()
        v = None
        if resp_value:
            k, v = resp_value
        return v

    @call
    def get_multi(self, keys):
        mem_cmd = '\r\n'
        for key in keys:
            mem_cmd = 'get %s %s'%(key ,mem_cmd)
        send(mem_cmd)
        resp_dict = {}
        for key in keys:
            # key and corresponding value from memcache
            resp_value = self._get_response()
            #resp_value can be None if key not found or k,v tuple
            if resp_value:
                k, v = resp_value
                resp_dict[k] = v
        return resp_dict

    def _handle_value(self, data):
        '''Handle function status for successful response for get key.
        data_size for the size of response i.e value of the key.
        '''
        data_size = int(data[-1])
        key = data[0]
        resp = receive(data_size)
        until_eol() # noop
        return key, resp

    def _handle_end(self, data):
        # Return memcache 'END' command.
        return 'END'

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
                handle_resp = getattr(self, '_handle_%s'%status.lower())(
                    resp_list[1:])
                if handle_resp == 'END':
                    handle_resp = self._get_response()
                return handle_resp
        else:
            raise MemCacheNotFoundError(e_message)

