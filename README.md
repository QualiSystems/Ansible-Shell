[![Coverage Status](https://coveralls.io/repos/github/QualiSystems/Ansible-Shell/badge.svg?branch=develop)](https://coveralls.io/github/QualiSystems/Ansible-Shell?branch=develop)
[![Code Climate](https://codeclimate.com/github/QualiSystems/Ansible-Shell/badges/gpa.svg)](https://codeclimate.com/github/QualiSystems/Ansible-Shell)
[![Dependency Status](https://dependencyci.com/github/QualiSystems/Ansible-Shell/badge)](https://dependencyci.com/github/QualiSystems/Ansible-Shell)

# Ansible-Shell-Extended
A CloudShell 'Shell' that allows integration with Ansible. This is an extended repo of the official configuration management package. 
Custom changes to driver and package have been added.

## Custom Param Overrides
The following configuration management parameters can be over-ridden by adding the following:
- REPO_URL
- REPO_USER
- REPO_PASSWORD (will be a plain text parameter)
- CONNECTION_METHOD

## Gitlab Support
- Gitlab links are supported, but for Private Repos require the URL to be in format of their REST api
- http://<SERVER_IP>/api/<API_VERSION>/projects/<PROJECT_ID>/repository/files/<PROJECT_PATH>/raw?ref=<GIT_BRANCH>
- example - http://10.160.7.7/api/v4/projects/4/repository/files/hello_world.sh/raw?ref=master
- The password field needs to be populated with gitlab access token, which will be sent along with request as header
- Access Token only needed for private repos, password field can be left blank for public repos
- The "User" field can be left blank for gitlab auth. Only access token needed
- Public Repos appear to work fine with both "raw" url link as well as the API formatted URL with no token
- Gitlab docs - https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html

## To Install
- Download python package from releases and place in local pypi server on Quali Server
    - Path: C:\Program Files (x86)\QualiSystems\CloudShell\Server\Config\Pypi Server Repository
- Delete venv (if it exists) to force creation of new venv with updated package
    - Path: C:\ProgramData\QualiSystems\venv\Ansible_Driver_{{driver_uid}}

## Changelog
- 25/06/2020 - Extending package to disable SSL Verification
- 25/12/2020 - Added Gitlab Support & Parameter Over-rides