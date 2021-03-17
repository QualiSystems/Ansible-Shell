import requests


class HttpRequestService(object):
    def get_response(self, url, auth):
        return requests.get(url, auth=(auth.username, auth.password) if auth else None, stream=True)
    
    def get_response_with_headers(self, url, headers):
        return requests.get(url, headers=headers, stream=True)
