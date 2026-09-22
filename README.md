# nemo-repo-columns

nemo-repo-columns is an extension for [Nemo](https://github.com/linuxmint/nemo),
the Cinnamon file manager, that adds "Git Branch" and "Git Status" columns to
the list view. Point Nemo at the directory where you keep your checkouts and
every repository shows its branch and how it stands against its upstream and
its working tree. It is a plugin for **nemo-repo-core** and needs it installed.

## Features

- **Git Branch**: the checked out branch, or `(detached)` on a detached HEAD.
- **Git Status**: a one line summary, with empty parts left out:

  | Part | Meaning |
  | --- | --- |
  | `N ahead` | Commits the upstream does not have |
  | `N behind` | Upstream commits you do not have |
  | `no upstream` | The branch does not track anything |
  | `N changed` | Staged plus unstaged changes |
  | `N untracked` | Files git does not track |
  | `clean` | None of the above |

  When git cannot read the repository, Git Branch shows `?` and Git Status
  shows the reason.
- Values are filled in for repository roots and left blank for every other
  folder, so mixed listings stay readable.
- Each column can be switched off in the config.
- Values update by themselves when `.git` changes; results are cached and
  shared with the other plugins through the core.

Example listing:

```
project-a     main       clean
project-b     feature/x  2 ahead, 3 changed
project-c     main       no upstream, 1 untracked
```

## Requirements

- nemo-repo-core 0.1.x
- Nemo with `nemo-python`, `git` in `PATH`

## Install and run

Install nemo-repo-core first (run `./install.sh` in its checkout), then from a
checkout of this repository:

```bash
./install.sh
nemo -q
```

Then turn the columns on: in list view right click the column headers, or set
the default for every folder under Edit > Preferences > List View.

`install.sh` links `nemoRepoColumns.py` into
`~/.local/share/nemo-python/extensions` and checks that it imports. Pass
`--copy` to copy instead of link. It stops with a message if nemo-repo-core is
not installed. No root is required.
`./uninstall.sh` removes the plugin.

## Configuration

Settings live in the shared file `~/.config/nemo-repo-core.json`.
`config.example.json` shows the keys this plugin uses:

```json
{
  "cache_ttl_seconds": 5,
  "columns": {
    "branch": true,
    "status": true
  }
}
```

| Key | Default | Meaning |
| --- | --- | --- |
| `columns.branch` | `true` | Offer the Git Branch column to Nemo |
| `columns.status` | `true` | Offer the Git Status column to Nemo |
| `cache_ttl_seconds` | `5` | Core setting: how stale a value can be when the change did not touch `.git` |

`columns` is read once, when Nemo loads the extension, so changing it needs
`nemo -q`.

## Tests

The tests use the standard library `unittest` and need PyGObject with the Nemo
typelib (`gir1.2-nemo-3.0`) and nemo-repo-core: an installed core, a checkout
of nemo-repo-core next to this one (`../nemo-repo-core`), or a path in
`NEMO_REPO_CORE_PATH`. Without the core the suite is skipped. Run them from the
repository root:

```bash
python3 -m unittest discover -s tests
```

They cover which columns are offered depending on the config, and the values
written for plain folders, broken repositories and real repositories that are
clean, ahead, behind, dirty, detached or nested. Tests that need git create
throwaway repositories in a temporary directory and are skipped when `git` is
not installed. The shared config is redirected to a temporary file, so your
real config is never touched.

## Project layout

```
nemoRepoColumns.py        the Nemo extension
config.example.json       keys used by this plugin
install.sh, uninstall.sh  per-user install
tests/
  support.py              temporary config, git helpers and core lookup
  testColumns.py          unittest suite
```

## Limitations

- Only repository roots get values; folders inside a checkout stay blank.
- Only local directories are handled; remote locations are skipped.
- Changing `columns` requires a Nemo restart.
- Worktrees and submodules (`.git` is a file) are refreshed only when the cache
  TTL expires, not immediately on change.

## License

MIT. See `LICENSE`.
