import json
import os
import sys
from argparse import ArgumentParser
from collections import defaultdict
from itertools import chain
from pprint import pformat, pprint

import jinja2

from jira.client import JiraClient
from jira.serializer import JiraEncoder


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("--host", default=os.getenv("JIRA_URL"))
    parser.add_argument("--api-key", default=os.getenv("JIRA_APIKEY"))

    subparsers = parser.add_subparsers()

    projects_parser = subparsers.add_parser("projects")
    projects_parser.add_argument("--template", default="projects")
    projects_parser.set_defaults(command=projects_command)

    issues_parser = subparsers.add_parser("issues")
    issues_parser.add_argument("--template", default="issues")
    issues_parser.add_argument("query", nargs="+")
    issues_parser.set_defaults(command=issues_command)

    return parser


def create_jira_client(url, apikey) -> JiraClient:
    return JiraClient(url=url, apikey=apikey)


def create_template(name) -> jinja2.Template:
    with open(os.path.join("templates", f"{name}.j2"), "rt") as stream:
        text = stream.read()
    env = jinja2.Environment()
    env.filters["pformat"] = lambda t: pformat(t)
    env.filters["json"] = lambda t: json.dumps(t, indent=2, ensure_ascii=False)

    template = env.from_string(text)
    return template


def projects_command(args):
    client = create_jira_client(args.host, args.api_key)
    projects = list(client.find_projects())

    template = create_template(args.template)
    text = template.render({"projects": projects, "item": projects})
    print(text)


def issues_command(args):
    client = create_jira_client(args.host, args.api_key)
    query = " ".join(args.query)
    issues = list(client.find_issues(query, fields="summary,updated,status,assignee"))

    template = create_template(args.template)
    text = template.render({"issues": issues, "item": issues})
    print(text)


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
