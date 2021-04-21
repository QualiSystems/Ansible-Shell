import requests


class HttpRequestService(object):
    def get_response(self, url, auth, verify_certificate):
        return requests.get(url, auth=(auth.username, auth.password) if auth else None, stream=True, verify=verify_certificate)
    
    def get_response_with_headers(self, url, headers, verify_certificate):
        return requests.get(url, headers=headers, stream=True, verify=verify_certificate)
