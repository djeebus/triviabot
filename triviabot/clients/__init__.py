import logging
import requests
import time
import ujson
import urllib


class RequestError(Exception):
    def __init__(self, method, url, params, data, status_code, response_text, error=None):
        self.status_code = status_code

        message = '[%s %s%s%s] %s: "%s" %s' % (
            method,
            url,
            '' if not params else '?' + urllib.urlencode(params.items()),
            '' if not data else ' ' + ujson.dumps(data),
            status_code,
            response_text,
            self.message)

        super(RequestError, self).__init__(message, error)


class RetryError(Exception):
    pass


class Timer(object):
    def __init__(self):
        self._begin = None
        self._end = None
        self.duration = None

    def __enter__(self):
        self._begin = time.time()
        return self

    def __exit__(self, *_):
        self._end = time.time()
        self.duration = (self._end - self._begin) * 1000


class BaseClient(object):
    ROOT_API_URL = None

    def __init__(self):
        self._session = requests.session()
        self._common_data = {}
        self._common_headers = {}
        self._common_params = {}
        self._logger = logging.getLogger(__name__)

    def validate_response(self, response):
        return response

    @staticmethod
    def _combine(instance, common):
        if not common:
            return instance

        if not instance:
            instance = {}

        instance.update(common)
        return instance

    def _make_request(self, method, url, params=None, data=None, headers=None, validate=True):
        full_url = self.ROOT_API_URL + url

        data = self._combine(data, self._common_data)
        headers = self._combine(headers, self._common_headers)
        params = self._combine(params, self._common_params)

        if isinstance(data, dict):
            headers = headers or {}
            headers['Content-Type'] = 'application/json'
            data = ujson.dumps(data)

        while True:
            with Timer() as timer:
                response = self._session.request(
                    method,
                    full_url,
                    params=params,
                    data=data,
                    headers=headers,
                )
            self._logger.info('[{method} {url}{params}][ms={ms}][status={status}]'.format(
                method=method,
                url=full_url,
                params='' if not params else '?' + urllib.urlencode(params.items()),
                ms=timer.duration,
                status=response.status_code,
            ))

            try:
                response.raise_for_status()
                if validate is False:
                    return response

                return self.validate_response(response)
            except RetryError as re:
                self._logger.warn('retrying request: %s' % re.message)
                continue
            except Exception as e:
                raise RequestError(
                    method, full_url, params, data,
                    response.status_code, response.text, e)
