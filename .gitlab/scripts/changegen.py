from datetime import datetime, timedelta
from os import path, remove
from re import match
from typing import Any, Dict, List

from gitlab import Gitlab
from verboselog import verbose

CHANGELOG_FILE = "CHANGELOG.md"


class _Entry:
    """
    Extracts the common elements of merge commits and git tags used to
    create the change history contents.  Elements extracted from the
    response are:

    hash - commit hash of commit or tag
    shorthash - first 8 chars of the hash
    description - description in the commit or the name of the tag
    is_tag - whether the hash is a tag or not
    """

    def __init__(self, response: Dict[str, Any]):
        if "merge_commit_sha" in response.keys():
            self.time: datetime = datetime.strptime(
                response["merged_at"][0:19], "%Y-%m-%dT%H:%M:%S"
            ).astimezone()
            self.hash: str = response["merge_commit_sha"]
            self.shorthash: str = response["merge_commit_sha"][0:8]
            self.description: str = (
                response["title"].replace('Resolve "', "").replace('"', "")
            )
            self.is_tag: bool = False
        elif "target" in response.keys():
            self.time: datetime = datetime.strptime(
                response["commit"]["committed_date"], "%Y-%m-%dT%H:%M:%S.%f%z"
            )
            self.hash: str = response["commit"]["id"]
            self.shorthash: str = response["commit"]["short_id"]
            self.description: str = response["name"]
            self.is_tag: bool = True

    def to_markdown(self) -> str:
        if self.is_tag:
            return f"## {self.description}\n"
        else:
            return f"- ```{self.shorthash} - {self.description}```\n"

    def __lt__(self, other: "_Entry") -> bool:
        # handle erroneous case with identical tags"
        if self.is_tag and other.is_tag and self.time == other.time:
            return self.description < other.description
        else:
            return self.time < other.time

    def __repr__(self) -> str:
        entry_type = "TAG" if self.is_tag else "COM"
        return f"Entry({entry_type}, {self.time}, {self.hash}, {self.description})"


class ChangeGen:
    """
    Generates lists of changes for use in the changelog updates or for
    merge request descriptions
    """

    def __init__(self, gitlab: Gitlab, verbose: bool = False):
        self.gl = gitlab
        self.verbose = verbose

    def _read_changelog(self) -> List[str]:
        temp = False
        if not path.exists(CHANGELOG_FILE):
            verbose(f"{CHANGELOG_FILE} not found, pulling from Gitlab")
            temp = True
            self.gl.get_file(CHANGELOG_FILE, CHANGELOG_FILE)
        with open(CHANGELOG_FILE) as file:
            lines = file.readlines()
        if temp:
            verbose(f"Removing temp {CHANGELOG_FILE}")
            remove(CHANGELOG_FILE)
        return lines

    def _get_last_hash(self, line: str) -> str:
        start = line.find("(") + 1
        end = line.find(")")
        return line[start:end]

    def _get_entries(self) -> List[_Entry]:
        entries: List[_Entry] = list()

        for response in self.gl.list_merge_requests(
            state="merged", target_branch="main"
        ):
            entries.append(_Entry(response))

        for response in self.gl.list_tags():
            if not match(r"v[0-9]+.[0-9]+.?[0-9]*", response["name"]):
                continue
            entry = _Entry(response)
            hashmatch = list(filter(lambda x: x.hash == entry.hash, entries))
            if hashmatch:
                entry.time = hashmatch[0].time + timedelta(seconds=1)
            entries.append(entry)

        # Entries retrieved are not in chronological order, sort before check
        entries.sort(reverse=True)
        return entries

    def generate(self) -> Dict[str, str]:
        """
        Generates content to use for changelogs.

        Content are merge commit titles in chronological order. Changelog
        generation will recreate the full changelog file content.

        Returns
        -------
        Dict[str, str]
            The content required to update the changelog file
        """
        current = self._read_changelog()
        last_hash = self._get_last_hash(current[0]) if current else ""

        # Return empty dict if nothing to update
        entries = self._get_entries()
        if last_hash == entries[0].hash:
            return dict()

        lines: List[str] = list()

        lines.append(f"[//]: # ({entries[0].hash})\n")
        lines.append("\n")
        lines.append("# DAML Change Log\n")

        # If we have a change and no release yet
        if not entries[0].is_tag:
            lines.append("## Pending Release\n")

        for entry in entries:
            if entry.hash == last_hash:
                break
            lines.append((entry.to_markdown()))

        # If we had a pending release we can drop this as there are new changes
        for oldline in current[3:]:
            if oldline == "## Pending Release\n":
                continue
            lines.append(oldline)

        content = "".join(lines)

        new_shorthash = entries[0].shorthash
        change: Dict[str, str] = dict()
        change["commit_message"] = f"Update CHANGELOG.md with {new_shorthash}"
        change["content"] = content

        return change