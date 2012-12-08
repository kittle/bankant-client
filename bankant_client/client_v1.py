from time import sleep
from urlparse import urljoin
#from json import loads, dumps

import requests

API_URL = "http://ec2-54-252-42-78.ap-southeast-2.compute.amazonaws.com/api/v1/"


class BankantAPI():

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def _request_get(self, url_suffix, **kw):
        url = urljoin(API_URL, url_suffix)
        r = requests.get(url,
                         auth=(self.username, self.password), **kw)
        return r

    def image_upload(self, filename):
        url = urljoin(API_URL, "image/upload")
        r = requests.post(url,
                          files={'image': open(filename, 'rb')},
                          auth=(self.username, self.password))
        assert r.status_code == 200, r.status_code
        ret = r.json
        assert ret["status"] == "OK"
        return str(ret["image_id"])

    def image_result(self, image_id, result_type='ofx'):
        """
        # curl works
        # python-request still tries to do basic auth for redirection
        # and get 400 "<Code>InvalidArgument</Code><Message>Either the Signature query string parameter or the Authorization header sho"
        # from AWS S3
        # so let emulate redirect two requests
        """
        assert result_type == 'ofx'
        r = self._request_get("image/result/{}".format(str(image_id)),
                              allow_redirects=False)
        assert r.status_code == 307, (r.status_code, r.headers, r.text)
        r = requests.get(r.headers['Location'])
        assert r.status_code == 200, (r.status_code, r.url, r.headers, r.text)
        return r.content

    def image_wait_result(self, image_id):
        for i in range(100):
            info = self.image_status(image_id)
            if info["is_processed"]:
                break
            sleep(i * 1.5)
        else:
            raise RuntimeError("Processing takes too long")
        return self.image_result(image_id)

    def image_status(self, image_id):
        r = self._request_get("image/status/{}".format(str(image_id)))
        assert r.status_code == 200, r.status_code
        return r.json

    def images(self):
        r = self._request_get("image/list")
        assert r.status_code == 200, r.status_code
        return r['images']

"""
class BankAntImage():

    def __init__(self, api, filename):
        self.image_id = None
        self.api = api
        self.filename = filename

    def process(self):
        self.image_id = self.api.image_upload(self.filename)

    def status(self):
        if self.image_id is None:
            return None
        return self.api.image_status(self.image_id)
"""