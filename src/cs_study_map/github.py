"""Read-only upstream access. Authentication is restricted to api.github.com."""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from .storage import StudyError, git_blob_sha, safe_relative
from .net import open_without_redirects


class GitHub:
    def __init__(self, repository, token=None):
        if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
            raise StudyError("Invalid GitHub owner/repository")
        self.repository = repository
        self.token = token

    def _get(self, url, limit=20_000_000):
        host = urllib.parse.urlparse(url).hostname
        if host not in {"api.github.com", "raw.githubusercontent.com"}:
            raise StudyError("Unexpected upstream host")
        headers = {"User-Agent": "cs-study-map/0.1", "Accept": "application/vnd.github+json"}
        if self.token and host == "api.github.com":
            headers["Authorization"] = "Bearer " + self.token
        for attempt in range(3):
            try:
                with open_without_redirects(urllib.request.Request(url, headers=headers), timeout=60) as response:
                    data = response.read(limit + 1)
                if len(data) > limit:
                    raise StudyError("Upstream response exceeds configured size limit")
                return data
            except urllib.error.HTTPError as exc:
                if exc.code in {429, 502, 503, 504} and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise StudyError(f"GitHub request failed (HTTP {exc.code}); check access/rate limits") from None
            except (urllib.error.URLError, TimeoutError):
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise StudyError("GitHub network request failed") from None

    def api(self, resource):
        return json.loads(self._get(f"https://api.github.com/repos/{self.repository}/{resource}"))

    def head(self, branch):
        result = self.api("commits/" + urllib.parse.quote(branch, safe=""))
        return result["sha"], result["commit"]["tree"]["sha"]

    def tree(self, sha):
        result = self.api(f"git/trees/{sha}?recursive=1")
        if not result.get("truncated"):
            return result["tree"]
        # A partial recursive response must never be interpreted as deletion.
        found = []
        pending = [("", sha)]
        while pending:
            prefix, subtree = pending.pop()
            node = self.api(f"git/trees/{subtree}")
            if node.get("truncated"):
                raise StudyError("GitHub returned an incomplete subtree; previous index retained")
            for item in node["tree"]:
                item = dict(item, path=prefix + item["path"])
                if item["type"] == "tree":
                    pending.append((item["path"] + "/", item["sha"]))
                else:
                    found.append(item)
        return found

    def download(self, commit, record, limit):
        path = safe_relative(record["path"])
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise StudyError("Downloads require an immutable upstream commit")
        if record.get("size", 0) > limit:
            raise StudyError("File exceeds configured download limit")
        url = f"https://raw.githubusercontent.com/{self.repository}/{commit}/{urllib.parse.quote(path, safe='/')}"
        data = self._get(url, limit)
        if git_blob_sha(data) != record["blob_sha"]:
            raise StudyError("Downloaded content does not match indexed Git blob")
        return data


def source_url(repository, commit, path):
    return f"https://github.com/{repository}/blob/{commit}/{urllib.parse.quote(path, safe='/')}"
