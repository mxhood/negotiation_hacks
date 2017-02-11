"""Generated client library for cloudresourcesearch version v1."""
# NOTE: This file is autogenerated and should not be edited by hand.
from apitools.base.py import base_api
from googlecloudsdk.third_party.apis.cloudresourcesearch.v1 import cloudresourcesearch_v1_messages as messages


class CloudresourcesearchV1(base_api.BaseApiClient):
  """Generated client library for service cloudresourcesearch version v1."""

  MESSAGES_MODULE = messages
  BASE_URL = u'https://cloudresourcesearch.googleapis.com/'

  _PACKAGE = u'cloudresourcesearch'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform', u'https://www.googleapis.com/auth/cloud-platform.read-only']
  _VERSION = u'v1'
  _CLIENT_ID = '1042881264118.apps.googleusercontent.com'
  _CLIENT_SECRET = 'x_Tw5K8nnjoRAqULM9PFAC2b'
  _USER_AGENT = 'x_Tw5K8nnjoRAqULM9PFAC2b'
  _CLIENT_CLASS_NAME = u'CloudresourcesearchV1'
  _URL_VERSION = u'v1'
  _API_KEY = None

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new cloudresourcesearch handle."""
    url = url or self.BASE_URL
    super(CloudresourcesearchV1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.resources = self.ResourcesService(self)

  class ResourcesService(base_api.BaseApiService):
    """Service class for the resources resource."""

    _NAME = u'resources'

    def __init__(self, client):
      super(CloudresourcesearchV1.ResourcesService, self).__init__(client)
      self._upload_configs = {
          }

    def Search(self, request, global_params=None):
      """Lists accessible Google Cloud Platform resources that match the query. A.
resource is accessible to the caller if they have the IAM .get permission
for it.

      Args:
        request: (CloudresourcesearchResourcesSearchRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (SearchResponse) The response message.
      """
      config = self.GetMethodConfig('Search')
      return self._RunMethod(
          config, request, global_params=global_params)

    Search.method_config = lambda: base_api.ApiMethodInfo(
        http_method=u'GET',
        method_id=u'cloudresourcesearch.resources.search',
        ordered_params=[],
        path_params=[],
        query_params=[u'orderBy', u'pageSize', u'pageToken', u'query'],
        relative_path=u'v1/resources:search',
        request_field='',
        request_type_name=u'CloudresourcesearchResourcesSearchRequest',
        response_type_name=u'SearchResponse',
        supports_download=False,
    )
