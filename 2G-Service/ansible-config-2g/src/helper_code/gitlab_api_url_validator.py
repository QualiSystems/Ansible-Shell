import re


BASE_PATH_SAMPLE = "http://<SERVER_IP>/api/4/projects/<PROJECT_ID>/repository/files"
FULL_PATH_SAMPLE = "http://<SERVER_IP>/api/4/projects/<PROJECT_ID>/repository/files/<PROJECT_PATH>/raw?ref=<GIT_BRANCH>"


def is_base_path_gitlab_api(url):
    """
    DETERMINE INTENT TO USE GITLAB FROM BASE PATH OF URL
    should be of the following form:
    http://192.168.85.62/api/{api_version}/projects/{project_id}/repository/files/{file_path}/raw?ref={git branch}
    ex input - http://192.168.85.62/api/v4/projects/4/repository/files/hello_world.sh/raw?ref=master
    :param str url: the user input url
    """
    base_path_pattern = "api/v\d/projects/\d/repository/files"
    matching = re.search(base_path_pattern, url)
    if not matching:
        return False
    return True


def validate_full_path_gitlab_url(url):
    """
    Validate gitlab URL and raise Exceptions
    :param url:
    :return:
    """
    # determine if url is gitlab
    is_gitlab_url = is_base_path_gitlab_api(url)
    if not is_gitlab_url:
        raise Exception("Gitlab Base Path validation failed. Should be of form '{}'".format(BASE_PATH_SAMPLE))

    # VALIDATE ENTIRE GITLAB URL STRING
    gitlab_api_pattern = "https?://.+/api/v\d/projects/\d/repository/files/.+/raw\?ref=.+"
    matching = re.match(gitlab_api_pattern, url)
    if not matching:
        sample_url = "http://<SERVER_IP>/api/4/projects/<PROJECT_ID>/repository/files/<PROJECT_PATH>/raw?ref=<GIT_BRANCH>"
        raise Exception("Gitlab Rest API URL failed validation. Should be of form: {}".format(FULL_PATH_SAMPLE))
    return True


if __name__ == "__main__":
    input_url = "http://192.168.85.62/api/v4/projects/4/repository/files/hello_world.sh/raw?ref=master"
    is_gitlab = is_base_path_gitlab_api(input_url)
    print(is_gitlab)