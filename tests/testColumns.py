import os
import unittest
from unittest import mock

import support
from support import (FakeNemoFile, commitFile, makeClonedRepository, makeDirectory,
                     makeRepository, requiresGit, resetSharedState, runGitCommand,
                     writeConfig, writeFile)

plugin = support.importPlugin("nemoRepoColumns")

from nemoRepoCore import coreConfig, repoCache


def fakeColumn(**properties):
    return properties


class ColumnTestCase(unittest.TestCase):

    def setUp(self):
        resetSharedState()
        self.addCleanup(resetSharedState)
        self.provider = plugin.RepoColumnProvider()

    def valuesFor(self, path, **fileOptions):
        nemoFile = FakeNemoFile(path, **fileOptions)
        self.provider.update_file_info(nemoFile)
        return nemoFile.attributes


class GetColumnsTests(ColumnTestCase):

    def columns(self):
        with mock.patch.object(plugin.Nemo, "Column", fakeColumn):
            return self.provider.get_columns()

    def testBothColumnsByDefault(self):
        columns = self.columns()
        self.assertEqual([column["name"] for column in columns],
                         ["NemoRepoColumns::branch", "NemoRepoColumns::status"])
        self.assertEqual([column["attribute"] for column in columns],
                         ["repo_branch", "repo_status"])
        self.assertEqual([column["label"] for column in columns],
                         ["Git Branch", "Git Status"])

    def testBranchColumnOff(self):
        writeConfig(coreConfig, {"columns": {"branch": False}})
        self.assertEqual([column["label"] for column in self.columns()], ["Git Status"])

    def testStatusColumnOff(self):
        writeConfig(coreConfig, {"columns": {"status": False}})
        self.assertEqual([column["label"] for column in self.columns()], ["Git Branch"])

    def testBothColumnsOff(self):
        writeConfig(coreConfig, {"columns": {"branch": False, "status": False}})
        self.assertEqual(self.columns(), [])

    def testDefaultsRegistered(self):
        self.assertEqual(coreConfig.section("columns"), {"branch": True, "status": True})


class NonRepositoryTests(ColumnTestCase):

    def testPlainFolderIsBlank(self):
        self.assertEqual(self.valuesFor(makeDirectory()),
                         {"repo_branch": "", "repo_status": ""})

    def testRegularFileIsSkipped(self):
        path = writeFile(makeDirectory(), "file.txt")
        self.assertEqual(self.valuesFor(path, isDirectory=False), {})

    def testRemoteFolderIsSkipped(self):
        self.assertEqual(self.valuesFor("/share", scheme="sftp"), {})

    def testBrokenRepositoryShowsReason(self):
        path = makeDirectory()
        writeFile(path, ".git", "gitdir: /nonexistent\n")
        values = self.valuesFor(path)
        self.assertEqual(values["repo_branch"], "?")
        self.assertIn(values["repo_status"], ("git status failed", "git not found in PATH"))


@requiresGit
class RepositoryValueTests(ColumnTestCase):

    def testRepositoryWithoutUpstream(self):
        self.assertEqual(self.valuesFor(makeRepository()),
                         {"repo_branch": "main", "repo_status": "no upstream"})

    def testCleanClone(self):
        seed, clone = makeClonedRepository()
        self.assertEqual(self.valuesFor(clone),
                         {"repo_branch": "main", "repo_status": "clean"})

    def testAheadWithChanges(self):
        seed, clone = makeClonedRepository()
        runGitCommand(["checkout", "-q", "-b", "feature/x", "--track", "origin/main"], clone)
        commitFile(clone, "work.txt", "work")
        writeFile(clone, "readme.txt", "modified\n")
        writeFile(clone, "notes.txt")
        self.assertEqual(self.valuesFor(clone), {
            "repo_branch": "feature/x",
            "repo_status": "1 ahead, 1 changed, 1 untracked",
        })

    def testBehind(self):
        seed, clone = makeClonedRepository()
        commitFile(seed, "remote.txt", "remote")
        runGitCommand(["push", "-q", "origin", "main"], seed)
        runGitCommand(["fetch", "-q"], clone)
        self.assertEqual(self.valuesFor(clone)["repo_status"], "1 behind")

    def testDetachedHead(self):
        repository = makeRepository()
        runGitCommand(["checkout", "-q", "--detach"], repository)
        self.assertEqual(self.valuesFor(repository)["repo_branch"], "(detached)")

    def testFolderInsideRepositoryIsBlank(self):
        repository = makeRepository()
        nested = os.path.join(repository, "src")
        os.mkdir(nested)
        self.assertEqual(self.valuesFor(nested),
                         {"repo_branch": "", "repo_status": ""})

    def testFileObjectIsRegisteredForRedraw(self):
        repository = makeRepository()
        nemoFile = FakeNemoFile(repository)
        self.provider.update_file_info(nemoFile)
        repoCache.invalidate(repository)
        self.assertEqual(nemoFile.invalidations, 1)


class DescriptionTests(ColumnTestCase):

    def testNameAndDescription(self):
        [entry] = self.provider.get_name_and_desc()
        self.assertTrue(entry.startswith("nemo-repo-columns:::"))


if __name__ == "__main__":
    unittest.main()
