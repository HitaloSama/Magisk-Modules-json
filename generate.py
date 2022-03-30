import os
import sys

import rapidjson as json
from github import Github

# Configuration
REPO_NAME = "Magisk-Modules-Repo"
REPO_TITLE = "Magisk Modules Repo"

# Initialize the GitHub objects
g = Github(os.environ["GH_TOKEN"])
user = g.get_user(REPO_NAME)
repos = user.get_repos()

# Skeleton for the repository
meta = {"name": REPO_TITLE, "last_update": int(user.updated_at.timestamp() * 1000), "modules": []}

# Iterate over all public repositories
for repo in repos:
    # It is possible that module.prop does not exist (meta repo)
    try:
        # Parse module.prop into a python object
        moduleprop_raw = repo.get_contents("module.prop").decoded_content.decode(
            "UTF-8"
        )
        moduleprop = {}
        for line in moduleprop_raw.splitlines():
            if "=" not in line:
                continue
            lhs, rhs = line.split("=", 1)
            moduleprop[lhs] = rhs

        # Get latest commit and commit date
        commit_sha = repo.get_commits()[0].sha
        commit = repo.get_commit(sha=commit_sha)
        commit_date = commit.commit.committer.date

        # Create meta module information
        module = {
            "id": moduleprop["id"],
            "last_update": int(commit_date.timestamp() * 1000),
            "prop_url": f"https://raw.githubusercontent.com/{repo.full_name}/{repo.default_branch}/module.prop",
            "zip_url": f"https://github.com/{repo.full_name}/archive/{repo.default_branch}.zip",
            "notes_url": f"https://raw.githubusercontent.com/{repo.full_name}/{repo.default_branch}/README.md",
        }

        # Append to skeleton
        meta["modules"].append(module)
    except BaseException:
        continue

# Save our final skeleton to modules.json
jdump = json.dumps(meta, indent=4, sort_keys=True)
with open("modules.json", "w", encoding="utf-8") as f:
    f.write(jdump)
