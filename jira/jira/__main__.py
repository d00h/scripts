import json
import os
import sys
from argparse import ArgumentParser
from collections import defaultdict
from itertools import chain
from pprint import pprint

from .client import JiraClient
from .serializer import JiraEncoder


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("--host", default=os.getenv("JIRA_URL"))
    parser.add_argument("--api-key", default=os.getenv("JIRA_APIKEY"))

    subparsers = parser.add_subparsers()

    projects_parser = subparsers.add_parser("projects")
    projects_parser.set_defaults(command=projects_command)

    issues_parser = subparsers.add_parser("issues")
    issues_parser.add_argument("query", nargs="+")
    issues_parser.set_defaults(command=issues_command)

    return parser


def create_jira_client(args) -> JiraClient:
    return JiraClient(url=args.host, apikey=args.api_key)


def projects_command(args):
    client = create_jira_client(args)
    for project in client.find_projects():
        print(project)


def issues_command(args):
    client = create_jira_client(args)
    query = " ".join(args.query)

    result = defaultdict(list)
    for issue in client.find_issues(query, fields="summary,updated,status,assignee"):
        result[issue.status].append(issue)

    issues = chain.from_iterable(
        sorted(status_issues, key=lambda i: i.updated_at, reverse=True)
        for status_issues in result.values()
    )
    issues = [issue.as_dict() for issue in issues]
    json_encoder = JiraEncoder(indent=2, ensure_ascii=False)
    print(json_encoder.encode(issues))


def main():
    parser = create_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    command = args.command
    command(args)


if __name__ == '__main__':
    main()
