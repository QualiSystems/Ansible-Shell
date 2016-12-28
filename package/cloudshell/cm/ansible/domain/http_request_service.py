import requests

class HttpRequestService(object):
    def get_request(self, url, auth):
        return requests.get(url, auth=(auth.username, auth.password) if auth else None, stream=True)