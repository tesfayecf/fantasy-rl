import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

"""
    # RequestManager Class

    The `RequestManager` class is a central component for managing HTTP requests within a program. 
    It encapsulates the implementation details associated with making HTTP requests, ensuring that 
    multiple requests can be efficiently handled simultaneously while maintaining a shared session 
    using the `requests` library. This class offers extensive configurability by allowing the setting 
    of custom headers, parameters, as well as the specification of default headers and bearer authentication tokens.

    ## Attributes

    - `session` (`requests.Session`): A shared session object used to manage multiple HTTP requests efficiently.
    - `default_headers` (`dict`): A dictionary of default headers that will be included in each request made using this manager.
    - `bearer_token` (`str`): An optional bearer authentication token to be included in requests for authentication purposes.
    - `session` (`requests.Session`): A shared session object used to manage multiple HTTP requests efficiently.
    - `max_workers` (`int`): The maximum number of threads to use for concurrent requests.

    ## Methods

    - `make_request(method: str, url: str, headers: dict = None, params: dict = None, data: dict = None, timeout: int = None, auth: Tuple = None, hooks: dict = None, proxies: dict = None, session: requests.Session = None) -> requests.Response`: Makes an HTTP request using the specified method, URL, and optional custom headers, parameters, and data. Returns the response object if the request is successful, or None in case of a failure.
    - `get(url: str, headers: dict = None, params: dict = None, timeout: int = None, auth: Tuple = None, hooks: dict = None, proxies: dict = None, session: requests.Session = None) -> requests.Response`: Makes a GET request.
    - `post(url: str, headers: dict = None, params: dict = None, data: dict = None, timeout: int = None, auth: Tuple = None, hooks: dict = None, proxies: dict = None, session: requests.Session = None) -> requests.Response`: Makes a POST request.
    
    ## Private Methods

    - `__close_session()`: Closes the shared session when it is no longer needed.

"""

class RequestManager:

    def __init__(self, default_headers: Dict = None, bearer_token: str = None, session: requests.Session = None, max_workers: int = 5):
        if session is None:
            self.session = requests.Session()
        else:
            self.session = session

        if bearer_token:
            self.session.headers['Authorization'] = f'Bearer {bearer_token}'

        if default_headers:
            self.session.headers.update(default_headers)

        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def __del_(self):
        self.__close_session()

    def get(self, url, headers=None, params=None, timeout=None, auth=None, hooks=None, proxies=None, session=None):
        return self.executor.submit(self.__make_request, 'GET', url, headers, params, timeout=timeout, auth=auth, hooks=hooks, proxies=proxies, session=session)

    def post(self, url, headers=None, params=None, timeout=None, auth=None, hooks=None, proxies=None, session=None):
        return self.executor.submit(self.__make_request, 'POST', url, headers, params, timeout=timeout, auth=auth, hooks=hooks, proxies=proxies, session=session)

    def setConfig(self, config):
        if 'headers' in config:
            self.session.headers.update(config['headers'])
        if 'params' in config:
            self.params = config['params']
        if 'bearer_token' in config:
            self.session.headers['Authorization'] = f'Bearer {config["bearer_token"]}'

    #######################
    ### Private Methods ###
    #######################

    def __make_request(self, method, url, headers=None, params=None, data=None, timeout=None, auth=None, hooks=None, proxies=None, session=None):
        session = session or self.session
        headers = headers or {}
        params = params or {}
        request_headers = {**headers}
        request_params = {**params}

        try:
            response = session.request(
                method,
                url,
                headers=request_headers,
                params=request_params,
                data=data,
                timeout=timeout,
                auth=auth,
                hooks=hooks,
                proxies=proxies
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        
    def __close_session(self):
        self.session.close()
        self.executor.shutdown(wait=True)