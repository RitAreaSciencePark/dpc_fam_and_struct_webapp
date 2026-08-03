# Semantic Versioning - DPCexplorer vX.Y.Z

This document explains how DPCexplorer implements the FAIR Principles for Research Software (FAIR4RS), and how a new release actually gets published, step by step. It is meant for maintainers who want to cut a new release, and for anyone curious about how the citation and archiving side of the project works.

## 1. Why this matters

Research software is easy to lose track of: a repository can be renamed, deleted, or simply abandoned, and any paper that cites "see our GitHub" then points nowhere. FAIR4RS exists to prevent that, by making software Findable, Accessible, Interoperable, and Reusable, the same way FAIR already applies to research data. For DPCexplorer, this is done through two things working together: a permanent archive on Zenodo, and a machine-readable citation file, `CITATION.cff`, kept at the root of the repository.

## 2. How the Zenodo and GitHub Integration Works

Zenodo is a free, CERN-operated archive for research outputs. It has a direct
integration with GitHub that automates the archiving step.

**One-time setup** (already done for this repository):

1. Sign in to [zenodo.org](https://zenodo.org) using your GitHub account.
2. Go to your Zenodo account's GitHub settings page and find the repository in the list of your GitHub repositories.
3. Toggle the switch for that repository to ON.

**What happens on every release**, once the toggle above is on:

1. You publish a new Release on GitHub (see Section 5).
2. Zenodo detects the release automatically, downloads a snapshot of the repository exactly as it was at that tag, and archives it.
3. Zenodo mints a brand-new DOI for that specific version. This is the **version DOI**, unique to that one release.
4. Zenodo also maintains a single **concept DOI** that never changes and always resolves to whichever version is the most recent. 
   For DPCexplorer, that concept DOI is [`10.5281/zenodo.20575268`](https://doi.org/10.5281/zenodo.20575268), the one printed in the "How to Cite This Work" section of the README and the one most people should cite by default.

There is a separate, second DOI in this project worth knowing about: [`10.5281/zenodo.20159208`](https://doi.org/10.5281/zenodo.20159208)
is not a software version DOI at all, it identifies the preprocessed dataset (the CSV, FASTA, and PDB files used to populate the database), deposited on Zenodo independently of the code releases.

## 3. CITATION.cff

`CITATION.cff` is a plain-text, machine-readable YAML file, following the Citation File Format, kept at the root of the repository. Two platforms read it automatically:

- **GitHub** detects it and shows a "Cite this repository" button on the repository page, which generates a ready-to-use citation directly from the file's content.
- **Zenodo** reads the same file when it archives a release, and uses it to prefill the record's metadata: title, authors, ORCID identifiers, license, keywords, and abstract, so this information does not need to be entered by hand on Zenodo for every release.


## 4. The Semantic Versionning Pattern `vX.Y.Z`

DPCexplorer's GitHub Releases follow the semantic versioning pattern, written as `vX.Y.Z`:

- **X** stands for a **major version**. Incremented for changes that break backward compatibility,
  for example a database schema change that makes an old exported file incompatible,
  or a URL structure change that breaks existing bookmarked links.
- **Y** stands for a **minor version**. Incremented when new functionality is added in a way that
  does not break anything already working, for example adding the new `api` app
  discussed in `DPCexplorer_API_Documentation.md`, or adding a new search filter.
- **Z** stands for a **Patch Versions**. Incremented for backward-compatible bug fixes,
  small corrections, or documentation updates, with no new features and nothing
  breaking.

In short: Increase the value of X when breaking the existing tool. Increase the value of Y when implementing new features in a backward-compatible way. Increase the value of Z when fixing bugs.

## 5. The Full Release Workflow, Step by Step

This is the sequence to follow whenever DPCexplorer is ready for a new citable
release.

**Step 1: finish and merge the work.** Develop on a branch as usual, commit your
changes, and get the work merged into `main`.

**Step 2: decide the new version number.** Look at what changed since the last tag
and decide whether it is a major, minor, or fix-level change, following Section 4.

**Step 3: update `CITATION.cff` by hand: Edit the `version` field and
the `date-released` field to match the release you are about to make:

```yaml
version: "v1.1.0"
date-released: "2026-08-03"
```

Commit this change with a clear message:

```bash
git add CITATION.cff
git commit -m "chore: bump version to v1.1.0"
git push origin main
```

**Step 4: create an annotated Git tag.** An annotated tag (using `-a`) is preferred
over a lightweight tag because it stores the tagger's name, date, and a message,
which matters for a citable release:

```bash
git tag -a v1.1.0 -m "DPCexplorer v1.1.0"
```

**Step 5: push the tag.** Tags are not pushed automatically with `git push`, they
need their own push:

```bash
git push origin v1.1.0
```

**Step 6: turn the tag into a GitHub Release.** Go to the repository on GitHub,
open **Releases**, click **Draft a new release**, choose the tag `v1.1.0` you just
pushed, give the release a title (commonly the same as the tag, for example
"DPCexplorer v1.1.0"), optionally write release notes describing what changed, and
click **Publish release**.

**Step 7: let Zenodo do its part automatically.** Because the GitHub and Zenodo
integration is already enabled for this repository (Section 2), publishing the
release triggers Zenodo to archive the exact state of the code at that tag and mint
a new version DOI. The existing concept DOI, `10.5281/zenodo.20575268`, automatically
starts resolving to this newest version instead of the previous one. No manual step
is needed on the Zenodo side for this to happen.

## 6. Verifying a Release Afterward

After Step 7, confirm everything worked as expected:

- Visit the concept DOI link, [`https://doi.org/10.5281/zenodo.20575268`](https://doi.org/10.5281/zenodo.20575268), and check
  that it now resolves to the new version.
- On the Zenodo record page, open the "Versions" panel and confirm the new
  version-specific DOI is listed alongside the earlier ones.
- On GitHub, click the "Cite this repository" button and confirm the displayed
  citation now shows the updated version number and date, which it reads directly
  from `CITATION.cff`.


## 7. Extending this later

Anyone taking over maintenance should keep three things in sync whenever a release goes out: the git tag, the GitHub release notes, and the `version`, `date-released` fields in `CITATION.cff`. As long as those three agree and the Zenodo connection stays active, the archiving and DOI minting described above will keep happening automatically, with no extra manual step beyond publishing the GitHub release.