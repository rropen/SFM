import json
from sfm.config import get_settings

app_settings = get_settings()


def mock_fetch_github_payload(test_int):
    file_list = [
        ["./test_converters/testing_files/wh_repo_created.json", "repository"],
        [
            "./test_converters/testing_files/wh_pull_request_dev.json",
            "pull_request",
        ],
        [
            "./test_converters/testing_files/wh_pull_request_main_not_merged.json",
            "pull_request",
        ],
        [
            "./test_converters/testing_files/wh_pull_request_main_merged.json",
            "pull_request",
        ],
        [
            "./test_converters/testing_files/wh_issue_opened.json",
            "issues",
        ],  # not currently important until flow metrics
        ["./test_converters/testing_files/wh_issue_labeled_prodDef.json", "issues"],
        ["./test_converters/testing_files/wh_issue_closed.json", "issues"],
        ["./test_converters/testing_files/wh_issue_reopened.json", "issues"],
        ["./test_converters/testing_files/wh_issue_unlabeled.json", "issues"],
        # ["./test_converters/testing_files/wh_deployment.json", "deployment"],
        ["./test_converters/testing_files/wh_repo_renamed.json", "repository"],
        ["./test_converters/testing_files/wh_repo_deleted.json", "repository"],
    ]
    payload = json.load(open(file_list[test_int][0]))
    proj_auth_token = app_settings.GITHUB_WEBHOOK_SECRET
    event_type = file_list[test_int][1]

    return payload, event_type, proj_auth_token


def mock_parse_github_for_repo_data():
    repo_data = json.load(open("./test_converters/testing_files/testing_repo.json"))
    return repo_data


def mock_parse_github_for_issue_events():
    issue_events = json.load(open("./test_converters/testing_files/issue_events.json"))
    return issue_events


def mock_parse_github_for_events():
    events = json.load(open("./test_converters/testing_files/events.json"))
    return events


def mock_get_commit_data():
    json_data = json.load(open("./test_converters/testing_files/commits.json"))
    return json_data
