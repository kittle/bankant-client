##INSTALL

```
pip install git+https://github.com/kittle/bankant-client.git
```

##Start with API
```
from bankant_client import BankantAPI

api = BankantAPI("user123", "pass123")
```

##Image Processing API

```

# upload image
image_id = api.image_upload("westpac_business_flexi.png")

#print api.image_status(image_id)

# wait for result and get it
print api.image_wait_result(image_id)
```

##User API
```
assert api.user_create('zzz', 'zzz1')
assert api.user_password('zzz', 'zzz2')
assert api.user_delete('zzz')
```
