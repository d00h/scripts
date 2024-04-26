from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass
class JiraResponse:

    start_at: int
    total: int
    max_results: int
    data: list

    def __iter__(self):
        return iter(self.data)

    @classmethod
    def from_dict(cls, data: dict, key: str):
        return cls(
            start_at=data.get("startAt"),
            total=data.get("Total"),
            max_results=data.get("maxResults"),
            data=data.get(key),
        )


def field(d: dict, *keys):
    result = d
    for key in keys:
        if result:
            result = result.get(key)
    return result


@dataclass
class JiraIssue:

    key: str
    summary: str
    status: str
    assignee: str
    updated_at: datetime

    def as_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "JiraIssue":
        try:
            data_fields = data["fields"]
            return cls(
                key=data["key"],
                summary=data_fields["summary"],
                status=field(data_fields, "status", "name") or "none",
                assignee=field(data_fields, "assignee", "name") or "",
                updated_at=datetime.fromisoformat(data_fields["updated"]),
            )
        except BaseException as ex:
            raise ValueError(data) from ex
