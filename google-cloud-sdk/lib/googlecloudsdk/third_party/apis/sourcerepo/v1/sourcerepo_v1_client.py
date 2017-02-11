"""Generated client library for sourcerepo version v1."""
# NOTE: This file is autogenerated and should not be edited by hand.
from apitools.base.py import base_api
from googlecloudsdk.third_party.apis.sourcerepo.v1 import sourcerepo_v1_messages as messages


class SourcerepoV1(base_api.BaseApiClient):
  """Generated client library for service sourcerepo version v1."""

  MESSAGES_MODULE = messages
  BASE_URL = u'https://sourcerepo.googleapis.com/'

  _PACKAGE = u'sourcerepo'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform']
  _VERSION = u'v1'
  _CLIENT_ID = '1042881264118.apps.googleusercontent.com'
  _CLIENT_SECRET = 'x_Tw5K8nnjoRAqULM9PFAC2b'
  _USER_AGENT = 'x_Tw5K8nnjoRAqULM9PFAC2b'
  _CLIENT_CLASS_NAME = u'SourcerepoV1'
  _URL_VERSION = u'v1'
  _API_KEY = None

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new sourcerepo handle."""
    url = url or self.BASE_URL
    super(SourcerepoV1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.projects_repos = self.ProjectsReposService(self)
    self.projects = self.ProjectsService(self)

  class ProjectsReposService(base_api.BaseApiService):
    """Service class for the projects_repos resource."""

    _NAME = u'projects_repos'

    def __init__(self, client):
      super(SourcerepoV1.ProjectsReposService, self).__init__(client)
      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      """Creates a repo in the given project with the given name..

If the named repository already exists, `CreateRepo` returns
`ALREADY_EXISTS`.

      Args:
        request: (SourcerepoProjectsReposCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Repo) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    Create.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1/projects/{projectsId}/repos',
        http_method=u'POST',
        method_id=u'sourcerepo.projects.repos.create',
        ordered_params=[u'parent'],
        path_params=[u'parent'],
        query_params=[],
        relative_path=u'v1/{+parent}/repos',
        request_field=u'repo',
        request_type_name=u'SourcerepoProjectsReposCreateRequest',
        response_type_name=u'Repo',
        supports_download=False,
    )

    def Delete(self, request, global_params=None):
      """Deletes a repo.

      Args:
        request: (SourcerepoProjectsReposDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Empty) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    Delete.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1/projects/{projectsId}/repos/{reposId}',
        http_method=u'DELETE',
        method_id=u'sourcerepo.projects.repos.delete',
        ordered_params=[u'name'],
        path_params=[u'name'],
        query_params=[],
        relative_path=u'v1/{+name}',
        request_field='',
        request_type_name=u'SourcerepoProjectsReposDeleteRequest',
        response_type_name=u'Empty',
        supports_download=False,
    )

    def Get(self, request, global_params=None):
      """Returns information about a repo.

      Args:
        request: (SourcerepoProjectsReposGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Repo) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    Get.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1/projects/{projectsId}/repos/{reposId}',
        http_method=u'GET',
        method_id=u'sourcerepo.projects.repos.get',
        ordered_params=[u'name'],
        path_params=[u'name'],
        query_params=[],
        relative_path=u'v1/{+name}',
        request_field='',
        request_type_name=u'SourcerepoProjectsReposGetRequest',
        response_type_name=u'Repo',
        supports_download=False,
    )

    def GetIamPolicy(self, request, global_params=None):
      """Gets the access control policy for a resource.
Returns an empty policy if the resource exists and does not have a policy
set.

      Args:
        request: (SourcerepoProjectsReposGetIamPolicyRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Policy) The response message.
      """
      config = self.GetMethodConfig('GetIamPolicy')
      return self._RunMethod(
          config, request, global_params=global_params)

    GetIamPolicy.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1/projects/{projectsId}/repos/{reposId}:getIamPolicy',
        http_method=u'GET',
        method_id=u'sourcerepo.projects.repos.getIamPolicy',
        ordered_params=[u'resource'],
        path_params=[u'resource'],
        query_params=[],
        relative_path=u'v1/{+resource}:getIamPolicy',
        request_field='',
        request_type_name=u'SourcerepoProjectsReposGetIamPolicyRequest',
        response_type_name=u'Policy',
        supports_download=False,
    )

    def List(self, request, global_params=None):
      """Returns all repos belonging to a project.

      Args:
        request: (SourcerepoProjectsReposListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListReposResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    List.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1/projects/{projectsId}/repos',
        http_method=u'GET',
        method_id=u'sourcerepo.projects.repos.list',
        ordered_params=[u'name'],
        path_params=[u'name'],
        query_params=[],
        relative_path=u'v1/{+name}/repos',
        request_field='',
        request_type_name=u'SourcerepoProjectsReposListRequest',
        response_type_name=u'ListReposResponse',
        supports_download=False,
    )

    def SetIamPolicy(self, request, global_params=None):
      """Sets the access control policy on the specified resource. Replaces any.
existing policy.

      Args:
        request: (SourcerepoProjectsReposSetIamPolicyRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Policy) The response message.
      """
      config = self.GetMethodConfig('SetIamPolicy')
      return self._RunMethod(
          config, request, global_params=global_params)

    SetIamPolicy.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1/projects/{projectsId}/repos/{reposId}:setIamPolicy',
        http_method=u'POST',
        method_id=u'sourcerepo.projects.repos.setIamPolicy',
        ordered_params=[u'resource'],
        path_params=[u'resource'],
        query_params=[],
        relative_path=u'v1/{+resource}:setIamPolicy',
        request_field=u'setIamPolicyRequest',
        request_type_name=u'SourcerepoProjectsReposSetIamPolicyRequest',
        response_type_name=u'Policy',
        supports_download=False,
    )

    def TestIamPermissions(self, request, global_params=None):
      """Returns permissions that a caller has on the specified resource.
If the resource does not exist, this will return an empty set of
permissions, not a NOT_FOUND error.

      Args:
        request: (SourcerepoProjectsReposTestIamPermissionsRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TestIamPermissionsResponse) The response message.
      """
      config = self.GetMethodConfig('TestIamPermissions')
      return self._RunMethod(
          config, request, global_params=global_params)

    TestIamPermissions.method_config = lambda: base_api.ApiMethodInfo(
        flat_path=u'v1/projects/{projectsId}/repos/{reposId}:testIamPermissions',
        http_method=u'POST',
        method_id=u'sourcerepo.projects.repos.testIamPermissions',
        ordered_params=[u'resource'],
        path_params=[u'resource'],
        query_params=[],
        relative_path=u'v1/{+resource}:testIamPermissions',
        request_field=u'testIamPermissionsRequest',
        request_type_name=u'SourcerepoProjectsReposTestIamPermissionsRequest',
        response_type_name=u'TestIamPermissionsResponse',
        supports_download=False,
    )

  class ProjectsService(base_api.BaseApiService):
    """Service class for the projects resource."""

    _NAME = u'projects'

    def __init__(self, client):
      super(SourcerepoV1.ProjectsService, self).__init__(client)
      self._upload_configs = {
          }
