DOMAIN = "ha-vrm"

ATTR_CLONES = "clones"
ATTR_CLONES_UNIQUE = "clones_unique"
ATTR_FORKS = "forks"
ATTR_LATEST_COMMIT_MESSAGE = "latest_commit_message"
ATTR_LATEST_COMMIT_SHA = "latest_commit_sha"
ATTR_LATEST_OPEN_ISSUE_URL = "latest_open_issue_url"
ATTR_LATEST_OPEN_PULL_REQUEST_URL = "latest_open_pull_request_url"
ATTR_LATEST_RELEASE_TAG = "latest_release_tag"
ATTR_LATEST_RELEASE_URL = "latest_release_url"
ATTR_OPEN_ISSUES = "open_issues"
ATTR_OPEN_PULL_REQUESTS = "open_pull_requests"
ATTR_PATH = "path"
ATTR_STARGAZERS = "stargazers"

ATTR_DEVICE_ICON = "device_icon"
ATTR_SITEID = "idSite"
ATTR_TOKEN = "token"
ATTR_USERID = "idUser"
ATTR_IDENTIFIER = "identifier"

PATH_LOGIN = "/v2/auth/login"
PATH_DIAG = "/v2/installations/{installationId}/diagnostics?count=1000"
PATH_DASH = "/v2/installations/{installationId}/dashboard"
PATH_SITES = "/v2/users/{userId}/navbar-sites?extended=1"

BASE_API_URL = "https://vrmapi.victronenergy.com/"

CONF_SITES = "installations"

REQUEST_TIMEOUT = 30