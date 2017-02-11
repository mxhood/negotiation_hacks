# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Constants for the dataproc tool."""

from googlecloudsdk.api_lib.compute import base_classes as compute_base
from googlecloudsdk.api_lib.compute import constants as compute_constants
from googlecloudsdk.api_lib.compute import utils as compute_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute import scope_prompter
from googlecloudsdk.core import properties
from googlecloudsdk.core import resolvers
from googlecloudsdk.core.credentials import http


# Copy into dataproc for cleaner separation
SCOPE_ALIASES = compute_constants.SCOPES
SCOPE_ALIASES_FOR_HELP = compute_constants.ScopesForHelp()


def ExpandScopeAliases(scopes):
  """Replace known aliases in the list of scopes provided by the user."""
  scopes = scopes or []
  expanded_scopes = []
  for scope in scopes:
    if scope in SCOPE_ALIASES:
      expanded_scopes += SCOPE_ALIASES[scope]
    else:
      # Validate scopes server side.
      expanded_scopes.append(scope)
  return sorted(expanded_scopes)


class ConfigurationHelper(object):
  """Helper that uses compute component logic to build GceConfiguration."""

  def __init__(self):
    """Updates required global state and constructs ConfigurationHelper."""
    holder = compute_base.ComputeApiHolder(base.ReleaseTrack.GA)
    zone_prop = properties.VALUES.compute.zone
    project_prop = properties.VALUES.core.project

    self.batch_url = holder.client.batch_url
    self._compute_client = holder.client
    self.project = project_prop.Get(required=True)
    self.resources = holder.resources
    self.resource_type = None
    self.http = http.Http()

    self.resources.SetParamDefault(
        'compute', None, 'project', resolvers.FromProperty(project_prop))
    self.resources.SetParamDefault(
        'compute', None, 'zone', resolvers.FromProperty(zone_prop))

  def _GetResourceUri(
      self, resource_name, collection, region=None, zone=None):
    """Convert a GCE resource short-name into a URI."""
    if not resource_name:
      # Resource must be optional and server-specified. Ignore it.
      return resource_name
    resource_ref = self.resources.Parse(
        resource_name,
        {'region': region, 'zone': zone},
        collection=collection)
    return resource_ref.SelfLink()

  def _GetZoneRef(self, cluster_name):
    """Get GCE zone resource prompting if necessary."""
    zone = properties.VALUES.compute.zone.Get()
    if not zone:
      _, zone = scope_prompter.PromptForScope(
          resource_name='cluster',
          underspecified_names=[cluster_name],
          scopes=[compute_scope.ScopeEnum.ZONE],
          default_scope=None,
          scope_lister=flags.GetDefaultScopeLister(
              self._compute_client, self.project))
      if not zone:
        # Still no zone, just raise error generated by this property.
        zone = properties.VALUES.compute.zone.Get(required=True)
    return self.resources.Parse(zone, collection='compute.zones')

  def ResolveGceUris(
      self,
      cluster_name,
      image,
      master_machine_type,
      worker_machine_type,
      network,
      subnetwork):
    """Build dict of GCE URIs for Dataproc cluster request."""
    zone_ref = self._GetZoneRef(cluster_name)
    zone = zone_ref.Name()
    region = compute_utils.ZoneNameToRegionName(zone)
    uris = {
        'image': self._GetResourceUri(image, 'compute.images'),
        'master_machine_type':
            self._GetResourceUri(
                master_machine_type, 'compute.machineTypes', zone=zone),
        'worker_machine_type':
            self._GetResourceUri(
                worker_machine_type, 'compute.machineTypes', zone=zone),
        'network': self._GetResourceUri(network, 'compute.networks'),
        'subnetwork':
            self._GetResourceUri(
                subnetwork, 'compute.subnetworks', region=region),
        'zone': zone_ref.SelfLink(),
    }
    return uris
