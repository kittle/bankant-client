import os.path
from time import sleep
from urlparse import urljoin
from json import loads, dumps

import dateutil.parser
import requests

API_URL = "http://ec2-54-252-42-78.ap-southeast-2.compute.amazonaws.com/api/v1/"


class BankantAPI():

    def __init__(self, username, password, api_url=None):
        self.username = username
        self.password = password
        self.api_url = api_url or API_URL

    def _request_get(self, url_suffix, **kw):
        url = urljoin(self.api_url, url_suffix)
        r = requests.get(url,
                         auth=(self.username, self.password), **kw)
        return r

    #    Image Processing

    def image_upload(self, filename, f=None):
        """
        upload image for processing
        NOTE: filename or (filename and file object f)"
        """
        url = urljoin(self.api_url, "image/upload")
        r = requests.post(url,
                          files={'image': (os.path.basename(filename),
                                           f if f else open(filename, 'rb'))},
                          auth=(self.username, self.password))
        assert r.status_code == 200, r.status_code
        ret = r.json
        assert ret["status"] == "OK"
        return str(ret["image_id"])

    def image_result(self, image_id, result_type='ofx'):
        """
        Get processing result.

        Implementation note:
        curl work in single request. python-request doesn't
        It seems python-request tried do basic auth for redirection url
        AWS S3 don't like it and retunrn: 400 "<Code>InvalidArgument</Code><Message>Either the Signature query string parameter or the Authorization header sho"
        so redirect emulated with two requests
        """
        assert result_type == 'ofx'
        r = self._request_get("image/result/{}".format(str(image_id)),
                              allow_redirects=False)
        assert r.status_code == 307, (r.status_code, r.headers, r.text)
        r = requests.get(r.headers['Location'])
        assert r.status_code == 200, (r.status_code, r.url, r.headers, r.text)
        return r.content

    def image_result_to_file(self, image_id, filename):
        """
        Download result and save to filename
        """
        result_type = filename.split('.', 2)[1].lower()
        result = self.image_result(image_id, result_type=result_type)
        open(filename, "wb").write(result)

    def image_wait_result(self, image_id):
        for i in range(100):
            info = self.image_status(image_id)
            if info["is_processed"]:
                break
            sleep(i * 1.5)
        else:
            raise RuntimeError("Processing takes too long")
        return self.image_result(image_id)

    @staticmethod
    def _adopt_status(status):
        if status.get("created"):
            status["created"] = dateutil.parser.parse(status["created"])
        if status.get("processed"):
            status["processed"] = dateutil.parser.parse(status["processed"])
        return status

    def image_status(self, image_id):
        r = self._request_get("image/status/{}".format(str(image_id)))
        assert r.status_code == 200, r.status_code
        return self._adopt_status(r.json)

    def images(self):
        r = self._request_get("image/list")
        assert r.status_code == 200, r.status_code
        #import pudb; pudb.set_trace()
        return map(self._adopt_status, r.json['images'])

    #    User Management

    def _request_user(self, method, data):
        url = urljoin(self.api_url, "user")
        r = requests.request(method, url,
                    data=dumps(data),
                    headers={'content-type': 'application/json'},
                    auth=(self.username, self.password))
        return r

    def user_create(self, username, password):
        r = self._request_user("post",
                        {'username': username, 'password': password})
        print r.content
        return r.status_code == 200

    def user_password(self, username, password):
        r = self._request_user("put",
                        {'username': username, 'password': password})
        return r.status_code == 200

    def user_delete(self, username):
        r = self._request_user("delete", {'username': username})
        return r.status_code == 200


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
