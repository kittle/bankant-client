bankant-client
==============

from client_v1 import BankantAPI

api = BankantAPI("user123", "pass123")

image_id = api.image_upload("westpac_business_flexi.png")

print api.image_status(image_id)

print api.image_wait_result(image_id)
