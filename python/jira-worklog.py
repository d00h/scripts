import json
import os
import re
import subprocess
import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests


def get_git_branch(working_directory: str) -> str:
    ret = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=working_directory,
        capture_output=True
    )
    if ret.returncode != 0:
        raise ValueError("cann't get branch")
    return ret.stdout.decode("utf-8").strip()


def parse_jira_issue(text: str) -> str | None:
    found = re.match(r"^(\w+\-\d+)(.*)$", text, re.MULTILINE)
    if found:
        return found.group(1).upper()


def parse_timedelta(text: str) -> timedelta | None:
    result = timedelta()
    for found in re.finditer(r"(\d+)([mhdMHD])", text, re.MULTILINE):
        value, dim = int(found.group(1)), found.group(2)
        match dim:
            case "m" | "M":
                result += timedelta(minutes=value)
            case "h" | "H":
                result += timedelta(hours=value)
            case "d" | "D":
                result += timedelta(days=value)
    if result != timedelta():
        return result


class JiraClient:

    def __init__(self, host: str, apikey: str):
        self.host = host
        self.apikey = apikey

    def add_worklog(self, issue: str, spent_time: timedelta, comment: str):
        """
           https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-post
        """
        started = datetime.now(tz=timezone.utc) - spent_time
        url = os.path.join(self.host, "rest", "api", "latest", "issue", issue, "worklog")
        query = {
            "adjustEstimate": "leave"
        }
        if query:
            url = url + "?" + urlencode(query)
        headers = {
            "Authorization": f"Bearer {self.apikey}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {
            "timeSpentSeconds": int(spent_time.total_seconds()),
            "comment": comment,
        }

        resp = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(payload)
        )
        resp.raise_for_status()


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    project_group = parser.add_argument_group("Project")
    project_group.add_argument(
        "--working-directory",
        default=os.getcwd(),
        help="default: current directory"
    )

    jira_group = parser.add_argument_group("Jira")
    jira_group.add_argument(
        "--host",
        default=os.getenv("JIRA_URL"),
        help="default: $JIRA_URL"
    )
    jira_group.add_argument(
        "--api-key",
        default=os.getenv("JIRA_APIKEY"),
        help="default: $JIRA_APIKEY"
    )

    parser.add_argument("spent_time", help="something like 30m 3h 1d")
    parser.add_argument("comment", nargs='*')
    return parser


def run(args):
    spent_time = parse_timedelta(args.spent_time)
    if spent_time is None:
        raise ValueError("cann't parse spent time")
    git_branch = get_git_branch(args.working_directory)
    if not git_branch:
        raise ValueError("cann't get git branch")
    jira_issue = parse_jira_issue(git_branch)
    if not jira_issue:
        raise ValueError(f"cann't get jira issue from branch '{git_branch}'")

    jira = JiraClient(host=args.host, apikey=args.api_key)
    jira.add_worklog(
        issue=jira_issue,
        spent_time=spent_time,
        comment=" ".join(w.strip() for w in args.comment)
    )
    print("Recorded")


def main():
    parser = create_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return

    try:
        args = parser.parse_args()
        run(args)
    except BaseException as ex:
        print(ex)


if __name__ == '__main__':
    main()
