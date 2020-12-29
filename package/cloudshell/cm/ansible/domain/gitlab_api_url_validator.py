import re


def is_gitlab_rest_url(url):
    """"
    should be of the following form:
    http://192.168.85.62/api/{api_version}/projects/{project_id}/repository/files/{file_path}/raw?ref={git branch}
    ex input - http://192.168.85.62/api/v4/projects/4/repository/files/hello_world.sh/raw?ref=master
    :param str url: the user input url
    """
    EXAMPLE = "http://<SERVER_IP>/api/4/projects/<PROJECT_ID>/repository/files/<PROJECT_PATH>/raw?ref=<GIT_BRANCH>"

    # DETERMINE INTENT TO USE GITLAB
    initial_pattern_check = "api/v\d/projects/\d/repository/files"
    matching = re.search(initial_pattern_check, url)
    if not matching:
        return False

    # VALIDATE ENTIRE GITLAB URL STRING
    gitlab_api_pattern = "https?://.+/api/v\d/projects/\d/repository/files/.+/raw\?ref=.+"
    matching = re.match(gitlab_api_pattern, url)
    if not matching:
        raise Exception("Gitlab Rest API URL failed validation. Should be of form: {}".format(EXAMPLE))

    return True


if __name__ == "__main__":
    input_url = "http://192.168.85.62/api/v4/projects/4/repository/files/hello_world.sh/raw?ref=master"
    is_gitlab = is_gitlab_rest_url(input_url)
    print(is_gitlab)