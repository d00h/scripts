import json
import sys
from os import getenv, path
from pprint import pprint
from typing import Iterable
from urllib.parse import urlencode

import requests

from .model import JiraIssue, JiraResponse


class JiraClient:

    def __init__(self, url, apikey):
        if not url:
            raise ValueError('no URL')
        self.url = url

        if not apikey:
            raise ValueError('no APIKEY')
        self.apikey = apikey

    def _get(self, uri, query: dict):
        url = path.join(self.url, uri)
        if query:
            url = url + "?" + urlencode(query)

        resp = requests.get(url, headers={'Authorization': f'Bearer {self.apikey}'})

        if not resp.ok:
            resp.raise_for_status()
        return resp

    def _post(self, uri, data: dict):
        url = path.join(self.url, uri)

        resp = requests.post(url, 
                             headers={'Authorization': f'Bearer {self.apikey}'}, 
                             data=data)

        if not resp.ok:
            resp.raise_for_status()
        return resp

    def find_projects(self):
        """ https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/ """
        resp = self._get('rest/api/latest/project', query={})
        return resp.json()

    def find_issues(self, jql, max_results=100, fields=None) -> Iterable[dict]:
        """ https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get """

        start_at = 0
        found = True

        query = {"jql": jql, "maxResults": max_results}
        if fields:
            query["fields"] = fields

        while found:
            resp = self._get("rest/api/latest/search", query={**query, "startAt": start_at})
            found = False
            for issue in JiraResponse.from_dict(resp.json(), "issues"):
                found = True
                yield issue
                start_at += 1

    def get_issue(self, issue):
        """ https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get """
        resp = self.request(f'rest/api/latest/issue/{issue}/')

        data = resp.json()

        fields = data.get('fields', {})
        key = data.get('key') or ''
        summary = fields.get('summary') or ''

        created = fields.get('created') or ''
        status = fields.get('status', {}).get('name') or ''
        description = fields.get('description') or ''
        assignee = fields.get('displayName') or ''
        url = path.join(self.url, 'browse', issue)

        return '\n'.join([
            f'# {key} {summary} ({status}) {assignee}',
            '',
            f'Created: {created}',
            '',
            url,
            '',
            description,
        ])
