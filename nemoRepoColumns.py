#!/usr/bin/python3
import importlib.util
import os
import sys


def _ensureCoreOnPath():
    if importlib.util.find_spec("nemoRepoCore") is not None:
        return
    dataHome = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    dataDirs = (os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share").split(":")
    for base in [dataHome] + dataDirs:
        candidate = os.path.join(base, "nemo-repo-core")
        if os.path.isdir(os.path.join(candidate, "nemoRepoCore")):
            sys.path.insert(0, candidate)
            return


_ensureCoreOnPath()

import gi

gi.require_version("Nemo", "3.0")
from gi.repository import GObject, Nemo

from nemoRepoCore import (coreConfig, findRepoRoot, localDirectoryPath,
                          repoCache, requireCore)

requireCore("0.1.0")

branchAttribute = "repo_branch"
statusAttribute = "repo_status"

pluginDefaults = {
    "columns": {
        "branch": True,
        "status": True,
    },
}

coreConfig.registerDefaults(pluginDefaults)


class RepoColumnProvider(GObject.GObject, Nemo.ColumnProvider,
                         Nemo.InfoProvider, Nemo.NameAndDescProvider):

    def get_columns(self):
        columns = []
        if coreConfig.sectionFlag("columns", "branch", True):
            columns.append(Nemo.Column(name="NemoRepoColumns::branch",
                                       attribute=branchAttribute,
                                       label="Git Branch",
                                       description="Checked out branch of the repository"))
        if coreConfig.sectionFlag("columns", "status", True):
            columns.append(Nemo.Column(name="NemoRepoColumns::status",
                                       attribute=statusAttribute,
                                       label="Git Status",
                                       description="Sync state with the upstream plus working tree state"))
        return columns

    def update_file_info(self, file):
        path = localDirectoryPath(file)
        if path is None:
            return

        repoRoot = findRepoRoot(path)
        if repoRoot is None:
            file.add_string_attribute(branchAttribute, "")
            file.add_string_attribute(statusAttribute, "")
            return

        repoCache.registerFileObject(repoRoot, file)
        info = repoCache.get(repoRoot)

        if info.error:
            file.add_string_attribute(branchAttribute, "?")
            file.add_string_attribute(statusAttribute, info.error)
            return

        file.add_string_attribute(branchAttribute, info.branchLabel)
        file.add_string_attribute(statusAttribute, info.summary)

    def get_name_and_desc(self):
        return ["nemo-repo-columns:::Git Branch and Git Status columns for the list view"]
