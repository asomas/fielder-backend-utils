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