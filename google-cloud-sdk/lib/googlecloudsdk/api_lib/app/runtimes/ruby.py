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

"""Fingerprinting code for the Ruby runtime."""

import os
import re
import subprocess
import textwrap

from gae_ext_runtime import ext_runtime

from googlecloudsdk.api_lib.app import ext_runtime_adapter
from googlecloudsdk.api_lib.app.images import config
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


NAME = 'Ruby'
ALLOWED_RUNTIME_NAMES = ('ruby', 'custom')

# This should be kept in sync with the default Ruby version specified in
# the base docker image.
PREFERRED_RUBY_VERSION = '2.3.0'

# Keep these up to date. You can find the latest versions by visiting
# rubygems.org and searching for "bundler" and for "foreman".
# Checking about once every month or two should be sufficient.
# (Last checked 2016-01-08.)
BUNDLER_VERSION = '1.11.2'
FOREMAN_VERSION = '0.78.0'

# Mapping from Gemfile versions to rbenv versions with patchlevel.
# Keep this up to date. The canonical version list can be found at
# https://github.com/sstephenson/ruby-build/tree/master/share/ruby-build
# Find the highest patchlevel for each version. (At this point, we expect
# only 2.0.0 to need updating, since earlier versions are end-of-lifed, and
# later versions don't seem to be using patchlevels.)
# Checking about once a quarter should be sufficient.
# (Last checked 2016-01-08.)
RUBY_VERSION_MAP = {
    '1.8.6': '1.8.6-p420',
    '1.8.7': '1.8.7-p375',
    '1.9.1': '1.9.1-p430',
    '1.9.2': '1.9.2-p330',
    '1.9.3': '1.9.3-p551',
    '2.0.0': '2.0.0-p648'
}

# Mapping from gems to libraries they expect.
# We should add to this list as we find more common cases.
GEM_PACKAGES = {
    'rgeo': ['libgeos-dev', 'libproj-dev']
}

APP_YAML_CONTENTS = textwrap.dedent("""\
    env: flex
    runtime: {runtime}
    entrypoint: {entrypoint}
    """)
DOCKERIGNORE_CONTENTS = textwrap.dedent("""\
    .dockerignore
    Dockerfile
    .git
    .hg
    .svn
    """)

DOCKERFILE_HEADER = textwrap.dedent("""\
    # This Dockerfile for a Ruby application was generated by gcloud.

    # The base Dockerfile installs:
    # * A number of packages needed by the Ruby runtime and by gems
    #   commonly used in Ruby web apps (such as libsqlite3)
    # * A recent version of NodeJS
    # * A recent version of the standard Ruby runtime to use by default
    # * The bundler and foreman gems
    FROM gcr.io/google_appengine/ruby
    """)
DOCKERFILE_DEFAULT_INTERPRETER = textwrap.dedent("""\
    # This Dockerfile uses the default Ruby interpreter installed and
    # specified by the base image.
    # If you want to use a specific ruby interpreter, provide a
    # .ruby-version file, then delete this Dockerfile and re-run
    # "gcloud app gen-config --custom" to recreate it.
    """)
DOCKERFILE_CUSTOM_INTERPRETER = textwrap.dedent("""\
    # Install ruby {{0}} if not already preinstalled by the base image
    RUN cd /rbenv/plugins/ruby-build && \\
        git pull && \\
        rbenv install -s {{0}} && \\
        rbenv global {{0}} && \\
        gem install -q --no-rdoc --no-ri bundler --version {0} && \\
        gem install -q --no-rdoc --no-ri foreman --version {1}
    ENV RBENV_VERSION {{0}}
    """.format(BUNDLER_VERSION, FOREMAN_VERSION))
DOCKERFILE_MORE_PACKAGES = textwrap.dedent("""\
    # Install additional package dependencies needed by installed gems.
    # Feel free to add any more needed by your gems.
    RUN apt-get update -y && \\
        apt-get install -y -q --no-install-recommends \\
            {0} \\
        && apt-get clean && rm /var/lib/apt/lists/*_*
    """)
DOCKERFILE_NO_MORE_PACKAGES = textwrap.dedent("""\
    # To install additional packages needed by your gems, uncomment
    # the "RUN apt-get update" and "RUN apt-get install" lines below
    # and specify your packages.
    # RUN apt-get update
    # RUN apt-get install -y -q (your packages here)
    """)
DOCKERFILE_GEM_INSTALL = textwrap.dedent("""\
    # Install required gems.
    COPY Gemfile Gemfile.lock /app/
    RUN bundle install --deployment && rbenv rehash
    """)
DOCKERFILE_ENTRYPOINT = textwrap.dedent("""\
    # Start application on port 8080.
    COPY . /app/
    ENTRYPOINT {0}
    """)

ENTRYPOINT_FOREMAN = 'foreman start web -p 8080'
ENTRYPOINT_PUMA = 'bundle exec puma -p 8080 -e deployment'
ENTRYPOINT_UNICORN = 'bundle exec unicorn -p 8080 -E deployment'
ENTRYPOINT_RACKUP = 'bundle exec rackup -p 8080 -E deployment config.ru'


class RubyConfigError(exceptions.Error):
  """Error during Ruby application configuration."""


class MissingGemfileError(RubyConfigError):
  """Gemfile is missing."""


class StaleBundleError(RubyConfigError):
  """Bundle is stale and needs a bundle install."""


class RubyConfigurator(ext_runtime.Configurator):
  """Generates configuration for a Ruby app."""

  def __init__(self, path, params, ruby_version, entrypoint, packages):
    """Constructor.

    Args:
      path: (str) Root path of the source tree.
      params: (ext_runtime.Params) Parameters passed through to the
        fingerprinters.
      ruby_version: (str) The ruby interpreter in rbenv format
      entrypoint: (str) The entrypoint command
      packages: ([str, ...]) A set of packages to install
    """
    self.root = path
    self.params = params
    self.ruby_version = ruby_version
    self.entrypoint = entrypoint
    self.packages = packages

    # Write messages to the console or to the log depending on whether we're
    # doing a "deploy."
    if params.deploy:
      self.notify = log.info
    else:
      self.notify = log.status.Print

  def GenerateConfigs(self):
    """Generates all config files for the module.

    Returns:
      (bool) True if files were written.
    """
    all_config_files = []
    if not self.params.appinfo:
      all_config_files.append(self._GenerateAppYaml())
    if self.params.custom or self.params.deploy:
      all_config_files.append(self._GenerateDockerfile())
      all_config_files.append(self._GenerateDockerignore())

    created = [config_file.WriteTo(self.root, self.notify)
               for config_file in all_config_files]
    if not any(created):
      self.notify('All config files already exist. No files generated.')

    return any(created)

  def GenerateConfigData(self):
    """Generates all config files for the module.

    Returns:
      list(ext_runtime.GeneratedFile):
        The generated files
    """
    if not self.params.appinfo:
      app_yaml = self._GenerateAppYaml()
      app_yaml.WriteTo(self.root, self.notify)

    all_config_files = []
    if self.params.custom or self.params.deploy:
      all_config_files.append(self._GenerateDockerfile())
      all_config_files.append(self._GenerateDockerignore())

    return [f for f in all_config_files
            if not os.path.exists(os.path.join(self.root, f.filename))]

  def _GenerateAppYaml(self):
    """Generates an app.yaml file appropriate to this application.

    Returns:
      (ext_runtime.GeneratedFile) A file wrapper for app.yaml
    """
    app_yaml = os.path.join(self.root, 'app.yaml')
    runtime = 'custom' if self.params.custom else 'ruby'
    app_yaml_contents = APP_YAML_CONTENTS.format(runtime=runtime,
                                                 entrypoint=self.entrypoint)
    app_yaml = ext_runtime.GeneratedFile('app.yaml', app_yaml_contents)
    return app_yaml

  def _GenerateDockerfile(self):
    """Generates a Dockerfile appropriate to this application.

    Returns:
      (ext_runtime.GeneratedFile) A file wrapper for Dockerignore
    """
    dockerfile_content = [DOCKERFILE_HEADER]
    if self.ruby_version:
      dockerfile_content.append(
          DOCKERFILE_CUSTOM_INTERPRETER.format(self.ruby_version))
    else:
      dockerfile_content.append(DOCKERFILE_DEFAULT_INTERPRETER)
    if self.packages:
      dockerfile_content.append(
          DOCKERFILE_MORE_PACKAGES.format(' '.join(self.packages)))
    else:
      dockerfile_content.append(DOCKERFILE_NO_MORE_PACKAGES)
    dockerfile_content.append(DOCKERFILE_GEM_INSTALL)
    dockerfile_content.append(
        DOCKERFILE_ENTRYPOINT.format(self.entrypoint))

    dockerfile = ext_runtime.GeneratedFile(config.DOCKERFILE,
                                           '\n'.join(dockerfile_content))
    return dockerfile

  def _GenerateDockerignore(self):
    """Generates a .dockerignore file appropriate to this application."""
    dockerignore = os.path.join(self.root, '.dockerignore')
    dockerignore = ext_runtime.GeneratedFile('.dockerignore',
                                             DOCKERIGNORE_CONTENTS)
    return dockerignore


def Fingerprint(path, params):
  """Check for a Ruby app.

  Args:
    path: (str) Application path.
    params: (ext_runtime.Params) Parameters passed through to the
      fingerprinters.

  Returns:
    (RubyConfigurator or None) Returns a configurator if the path contains a
    Ruby app, or None if not.
  """
  appinfo = params.appinfo

  if not _CheckForRubyRuntime(path, appinfo):
    return None

  bundler_available = _CheckEnvironment(path)
  gems = _DetectGems(bundler_available)
  ruby_version = _DetectRubyInterpreter(path, bundler_available)
  packages = _DetectNeededPackages(gems)

  if appinfo and appinfo.entrypoint:
    entrypoint = appinfo.entrypoint
  else:
    default_entrypoint = _DetectDefaultEntrypoint(path, gems)
    entrypoint = _ChooseEntrypoint(default_entrypoint, appinfo)

  return RubyConfigurator(path, params, ruby_version, entrypoint, packages)


def _CheckForRubyRuntime(path, appinfo):
  """Determines whether to treat this application as runtime:ruby.

  Honors the appinfo runtime setting; otherwise looks at the contents of the
  current directory and confirms with the user.

  Args:
    path: (str) Application path.
    appinfo: (apphosting.api.appinfo.AppInfoExternal or None) The parsed
      app.yaml file for the module if it exists.

  Returns:
    (bool) Whether this app should be treated as runtime:ruby.
  """
  if appinfo and appinfo.GetEffectiveRuntime() == 'ruby':
    return True

  log.info('Checking for Ruby.')

  gemfile_path = os.path.join(path, 'Gemfile')
  if not os.path.isfile(gemfile_path):
    return False

  got_ruby_message = 'This looks like a Ruby application.'
  if console_io.CanPrompt():
    return console_io.PromptContinue(
        message=got_ruby_message,
        prompt_string='Proceed to configure deployment for Ruby?')
  else:
    log.info(got_ruby_message)
    return True


def _CheckEnvironment(path):
  """Gathers information about the local environment, and performs some checks.

  Args:
    path: (str) Application path.

  Returns:
    (bool) Whether bundler is available in the environment.

  Raises:
    RubyConfigError: The application is recognized as a Ruby app but
    malformed in some way.
  """
  if not os.path.isfile(os.path.join(path, 'Gemfile')):
    raise MissingGemfileError('Gemfile is required for Ruby runtime.')

  gemfile_lock_present = os.path.isfile(os.path.join(path, 'Gemfile.lock'))
  bundler_available = _SubprocessSucceeds('bundle version')

  if bundler_available:
    if not _SubprocessSucceeds('bundle check'):
      raise StaleBundleError('Your bundle is not up-to-date. '
                             "Install missing gems with 'bundle install'.")
    if not gemfile_lock_present:
      msg = ('\nNOTICE: We could not find a Gemfile.lock, which suggests this '
             'application has not been tested locally, or the Gemfile.lock has '
             'not been committed to source control. We have created a '
             'Gemfile.lock for you, but it is recommended that you verify it '
             'yourself (by installing your bundle and testing locally) to '
             'ensure that the gems we deploy are the same as those you tested.')
      log.status.Print(msg)
  else:
    msg = ('\nNOTICE: gcloud could not run bundler in your local environment, '
           "and so its ability to determine your application's requirements "
           'will be limited. We will still attempt to deploy your application, '
           'but if your application has trouble starting up due to missing '
           'requirements, we recommend installing bundler by running '
           '[gem install bundler]')
    log.status.Print(msg)

  return bundler_available


def _DetectRubyInterpreter(path, bundler_available):
  """Determines the ruby interpreter and version expected by this application.

  Args:
    path: (str) Application path.
    bundler_available: (bool) Whether bundler is available in the environment.

  Returns:
    (str or None) The interpreter version in rbenv (.ruby-version) format, or
    None to use the base image default.
  """
  if bundler_available:
    ruby_info = _RunSubprocess('bundle platform --ruby')
    if not re.match('^No ', ruby_info):
      match = re.match(r'^ruby (\d+\.\d+(\.\d+)?)', ruby_info)
      if match:
        ruby_version = match.group(1)
        ruby_version = RUBY_VERSION_MAP.get(ruby_version, ruby_version)
        msg = ('\nUsing Ruby {0} as requested in the Gemfile.'.
               format(ruby_version))
        log.status.Print(msg)
        return ruby_version
      # TODO(user): Identify other interpreters
      msg = 'Unrecognized platform in Gemfile: [{0}]'.format(ruby_info)
      log.status.Print(msg)

  ruby_version = _ReadFile(path, '.ruby-version')
  if ruby_version:
    ruby_version = ruby_version.strip()
    msg = ('\nUsing Ruby {0} as requested in the .ruby-version file'.
           format(ruby_version))
    log.status.Print(msg)
    return ruby_version

  msg = ('\nNOTICE: We will deploy your application using a recent version of '
         'the standard "MRI" Ruby runtime by default. If you want to use a '
         'specific Ruby runtime, you can create a ".ruby-version" file in this '
         'directory. (For best performance, we recommend MRI version {0}.)'.
         format(PREFERRED_RUBY_VERSION))
  log.status.Print(msg)
  return None


def _DetectGems(bundler_available):
  """Returns a list of gems requested by this application.

  Args:
    bundler_available: (bool) Whether bundler is available in the environment.

  Returns:
    ([str, ...]) A list of gem names.
  """
  gems = []
  if bundler_available:
    for line in _RunSubprocess('bundle list').splitlines():
      match = re.match(r'\s*\*\s+(\S+)\s+\(', line)
      if match:
        gems.append(match.group(1))
  return gems


def _DetectDefaultEntrypoint(path, gems):
  """Returns the app server expected by this application.

  Args:
    path: (str) Application path.
    gems: ([str, ...]) A list of gems used by this application.

  Returns:
    (str) The default entrypoint command, or the empty string if unknown.
  """
  procfile_path = os.path.join(path, 'Procfile')
  if os.path.isfile(procfile_path):
    return ENTRYPOINT_FOREMAN

  if 'puma' in gems:
    return ENTRYPOINT_PUMA
  elif 'unicorn' in gems:
    return ENTRYPOINT_UNICORN

  configru_path = os.path.join(path, 'config.ru')
  if os.path.isfile(configru_path):
    return ENTRYPOINT_RACKUP

  return ''


def _ChooseEntrypoint(default_entrypoint, appinfo):
  """Prompt the user for an entrypoint.

  Args:
    default_entrypoint: (str) Default entrypoint determined from the app.
    appinfo: (apphosting.api.appinfo.AppInfoExternal or None) The parsed
      app.yaml file for the module if it exists.

  Returns:
    (str) The actual entrypoint to use.

  Raises:
    RubyConfigError: Unable to get entrypoint from the user.
  """
  if console_io.CanPrompt():
    if default_entrypoint:
      prompt = ('\nPlease enter the command to run this Ruby app in '
                'production, or leave blank to accept the default:\n[{0}] ')
      entrypoint = console_io.PromptResponse(prompt.format(default_entrypoint))
    else:
      entrypoint = console_io.PromptResponse(
          '\nPlease enter the command to run this Ruby app in production: ')
    entrypoint = entrypoint.strip()
    if not entrypoint:
      if not default_entrypoint:
        raise RubyConfigError('Entrypoint command is required.')
      entrypoint = default_entrypoint
    if appinfo:
      # We've got an entrypoint and the user had an app.yaml that didn't
      # specify it.
      # TODO(mmuller): Offer to edit the user's app.yaml
      msg = ('\nTo avoid being asked for an entrypoint in the future, please '
             'add it to your app.yaml. e.g.\n  entrypoint: {0}'.
             format(entrypoint))
      log.status.Print(msg)
    return entrypoint
  else:
    msg = ("This appears to be a Ruby app. You'll need to provide the full "
           'command to run the app in production, but gcloud is not running '
           'interactively and cannot ask for the entrypoint{0}. Please either '
           'run gcloud interactively, or create an app.yaml with '
           '"runtime:ruby" and an "entrypoint" field.'.
           format(ext_runtime_adapter.GetNonInteractiveErrorMessage()))
    raise RubyConfigError(msg)


def _DetectNeededPackages(gems):
  """Determines additional apt-get packages required by the given gems.

  Args:
    gems: ([str, ...]) A list of gems used by this application.

  Returns:
    ([str, ...]) A sorted list of strings indicating packages to install
  """
  package_set = set()
  for gem in gems:
    if gem in GEM_PACKAGES:
      package_set.update(GEM_PACKAGES[gem])
  packages = list(package_set)
  packages.sort()
  return packages


def _RunSubprocess(cmd):
  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
  if p.wait() != 0:
    raise RubyConfigError('Unable to run script: [{0}]'.format(cmd))
  return p.stdout.read()


def _SubprocessSucceeds(cmd):
  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
  return p.wait() == 0


def _ReadFile(root, filename, required=False):
  path = os.path.join(root, filename)
  if not os.path.isfile(path):
    if required:
      raise RubyConfigError(
          'Could not find required file: [{0}]'.format(filename))
    return None
  with open(path) as f:
    return f.read()
