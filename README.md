# fielder-backend-utils

To install it in other project, you can simply do:

```
pip install git+https://github.com/asomas/fielder-backend-utils.git --no-cache-dir
```

or add entry in `requirements.txt`:

```
git+https://github.com/asomas/fielder-backend-utils.git@main#egg=fielder-backend-utils
```

> `main` is the branch name. It can be replaced with tag or release as well

To test the installation:

```
import fielder_backend_utils

fielder_backend_utils.hello_fielder()
```

## Testing

To run unit tests:

```
python setup.py test
```

## Auth local mode

When environment variable `ASOMAS_SERVER_MODE` is set to `local` or `test`, `@auth.auth` decorator **will not** call Firebase/Google authentication server to validate the token. It will just decode the JWT token and return object that has similar property as in normal mode. In order to generate acceptable JWT token, use tool like [jwt.io](https://jwt.io/) to encode payload (with HS256 algorithm) with following formats:

**Fielder Worker**

```
{
   "user_id": "xTzBP55WORk35TdZLIyFMtdD8N1a",
   "phone_number": "+441122334455"
}
```

> `user_id` corresponds to `workers` document id

**Fielder Organisation**

```
{
   "user_id": "xTzBP55WORk35TdZLIyFMtdD8N1a",
   "email": "jane@asomas.com"
}
```

> `user_id` corresponds to `organisations` document id

**OIDC/Service-to-service**

```
{
    "email": "fielder-dev-285511@appspot.gserviceaccount.com"
}
```

> `email` corresponds to service account email
