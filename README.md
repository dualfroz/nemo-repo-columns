# nemo-repo-columns

"Git Branch" and "Git Status" columns for the list view in
[Nemo](https://github.com/linuxmint/nemo), the Cinnamon file manager.

Point Nemo at the directory where you keep your checkouts, switch to list view,
and every repository shows its branch and how it stands:

```
project-a     main       clean
project-b     feature/x  2 ahead, 3 changed
project-c     main       1 behind, no upstream
```

Both columns can be sorted, so "everything with local changes" is one click on
the Git Status header.

Values are computed for repository roots and left blank for everything else, so
mixing repositories and ordinary folders in one listing stays readable.

## Requirements

- [nemo-repo-core](https://github.com/dualfroz/nemo-repo-core) 1.x
- Nemo with `nemo-python`, `git` in `PATH`

## Install

```bash
git clone https://github.com/dualfroz/nemo-repo-core
cd nemo-repo-core && ./install.sh && cd ..

git clone https://github.com/dualfroz/nemo-repo-columns
cd nemo-repo-columns && ./install.sh

nemo -q
```

Then turn the columns on: in list view, right click the column headers, or use
Edit > Preferences > List View to set the default for every folder.

`install.sh` links the plugin into `~/.local/share/nemo-python/extensions` and
checks that it imports. Pass `--copy` to copy instead of link. `./uninstall.sh`
removes it. Nothing is written outside your home directory and no root is
required.

## What the columns say

**Git Branch** is the checked out branch, or `(detached)` on a detached HEAD.

**Git Status** is a summary, in this order, with empty parts left out:

| Part | Meaning |
| --- | --- |
| `N ahead` | Commits the upstream does not have |
| `N behind` | Commits you do not have |
| `no upstream` | The branch is not tracking anything |
| `N changed` | Staged plus unstaged modifications |
| `N untracked` | Files git does not know about |
| `clean` | None of the above |

A repository git cannot read shows `?` and the reason.

## Configuration

Shared file, read live:

```
~/.config/nemo-repo-core.json
```

```json
{
  "cache_ttl_seconds": 5,
  "columns": {
    "branch": true,
    "status": true
  }
}
```

`columns` decides which of the two are offered to Nemo at all. Unlike every
other setting in this family it is read once at startup, because Nemo asks for
the column list when it loads the extension, so changing it needs `nemo -q`.

`cache_ttl_seconds` (core setting, default 5) bounds how stale a value can be
when the change did not touch `.git`. Changes inside `.git`, such as a commit
or a fetch, update the columns immediately.

## Notes

- Listing a directory of repositories runs one `git status` per repository, not
  one per row: results are cached and shared with the other plugins in this
  family.
- Only repository roots get values. A folder inside a checkout is left blank on
  purpose, so a source tree does not repeat the same branch on every row.

## Migrating from the single file version

These columns used to be part of `nemo_repo_emblems.py`, one file that also
provided emblems, a properties tab and a context menu. They are now separate
plugins on a shared core.

The one visible change: ahead and behind used to be written with arrows, and
are now written as `2 ahead, 1 behind`.

Your config carries over automatically, `~/.config/nemo-repo-emblems.json` is
copied to `~/.config/nemo-repo-core.json` on first run and the old file is left
alone. Remove the old extension so nothing is drawn twice:

```bash
rm ~/.local/share/nemo-python/extensions/nemo_repo_emblems.py
nemo -q
```

## Tested on

Linux Mint 22.2 (Zara), Cinnamon 6.4.14, Nemo 6.4.5, python-nemo 6.4.0,
Python 3.12.3.

## License

MIT. See `LICENSE`.
