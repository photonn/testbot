# testbot
a test echo app with python to be used to test an azure bot

the curl to call it should be something like:

curl -X POST https://<your-app-service-name>.azurewebsites.net/api/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello Azure Bot!"}'

### Configuration endpoint security

If the environment variable `CONFIG_TOKEN` is set, the `/config` endpoint requires an `Authorization` header with the value `Bearer <CONFIG_TOKEN>`.
