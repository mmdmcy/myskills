"""Tests for doc_check.py: python3 -I -m unittest discover -s notetaker/scripts/tests

Each structure rule has a passing case and a refused input; a repository that
sets no new key sees no new finding.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "doc_check.py"
spec = importlib.util.spec_from_file_location("doc_check", SCRIPT)
doc_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doc_check)

TODAY = date(2026, 11, 6)
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}


def write(root, files):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def commit(root, when, message="change"):
    """Commit everything in root as of the date `when` (git needs a repo once)."""
    env = {**GIT_ENV, "GIT_AUTHOR_DATE": f"{when}T12:00:00", "GIT_COMMITTER_DATE": f"{when}T12:00:00"}
    if not (root / ".git").exists():
        subprocess.run(["git", "init", "-q", str(root)], check=True, env=env)
    for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", "commit", "-q", "-m", message]):
        subprocess.run(["git", "-C", str(root), *args], check=True, env=env)


def findings(root, config, **kw):
    # reach: [] keeps the reachability rule out of fixtures that test another rule.
    found, notices, triggers = doc_check.check(root, {"reach": [], **config}, today=TODAY, **kw)
    return [f for f, _ in found], notices, triggers


STATE_PAGE = "# Apps\n\nState as of: 2026-11-01\nOwner: the owner\n\nText.\n"
DECISION = "# {n} - Title\n\nDate: 2026-11-01\nStatus: Accepted 2026-11-01\nDecider: the owner\n\n## Context\n"
REFERENCE = "# Mistral\n\nChecked on: {checked}\nRe-check: every 3 months\nRe-check: when Mistral announces a model\nSources: https://example.com (read {checked})\nOwner: docs/handbook/ai.md\n\n- ({checked}) a fact\n"


class DocCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_new_key_no_new_finding(self):
        write(self.root, {
            "AGENTS.md": "# Repo\n",
            "notes/stray.md": "# Stray\n",
            "docs/decisions/0001-a.md": "# 0001\n", "docs/decisions/0003-b.md": "# 0003\n",
            "docs/reports/undated.md": "## Found on 2026-01-01\n",
            "docs/reference/x.md": "# X\n",
        })
        found, notices, triggers = doc_check.check(self.root, {"skip": ["docs/"]}, today=TODAY)
        self.assertEqual((found, notices, triggers), ([], [], []))

    def test_reach_whole_repository_with_patterns(self):
        write(self.root, {
            "AGENTS.md": "# Repo\n\n- `apps/<app>/README.md`: one app\n- `docs/guide-*.md`: guides\n",
            "apps/a/README.md": "# A\n", "apps/b/README.md": "# B\n",
            "docs/guide-one.md": "# One\n",
            "notes/stray.md": "# Stray\n",
        })
        found, _, _ = findings(self.root, {"reach": ["."], "patterns": True})
        self.assertEqual(found, ["notes/stray.md"])
        found, _, _ = findings(self.root, {"reach": ["."]})
        self.assertEqual(sorted(found), ["apps/a/README.md", "apps/b/README.md", "docs/guide-one.md", "notes/stray.md"])
        found, _, _ = findings(self.root, {"reach": ["docs/"]})
        self.assertEqual(found, ["docs/guide-one.md"])

    def test_state_header(self):
        write(self.root, {"docs/handbook/apps.md": STATE_PAGE})
        found, _, _ = findings(self.root, {"state": ["docs/handbook/"]})
        self.assertEqual(found, [])
        write(self.root, {
            "docs/handbook/future.md": STATE_PAGE.replace("2026-11-01", "2027-01-01"),
            "docs/handbook/no-owner.md": "# X\n\nState as of: 2026-11-01\n",
            "docs/handbook/report.md": STATE_PAGE + "\n## Checked on 2026-11-02\n",
            "docs/handbook/bad-date.md": STATE_PAGE.replace("2026-11-01", "2026-13-01"),
        })
        found, _, _ = findings(self.root, {"state": ["docs/handbook/"]})
        self.assertEqual(sorted(found), ["docs/handbook/bad-date.md", "docs/handbook/future.md", "docs/handbook/no-owner.md", "docs/handbook/report.md"])

    def test_state_date_trails_last_commit(self):
        write(self.root, {"docs/handbook/apps.md": STATE_PAGE})
        commit(self.root, date(2026, 11, 5))
        self.assertEqual(findings(self.root, {"state": ["docs/handbook/"]})[0], [])
        write(self.root, {"docs/handbook/apps.md": STATE_PAGE + "More.\n"})
        commit(self.root, date(2026, 11, 20))
        found, _, _ = findings(self.root, {"state": ["docs/handbook/"]})
        self.assertEqual(found, ["docs/handbook/apps.md"])
        self.assertEqual(findings(self.root, {"state": ["docs/handbook/"], "state_grace_days": 30})[0], [])

    def test_decisions(self):
        write(self.root, {
            "docs/decisions/0001-a.md": DECISION.format(n="0001") + "Status: Superseded by 0002\n",
            "docs/decisions/0002-b.md": DECISION.format(n="0002"),
            "docs/decisions/TEMPLATE.md": "# NNNN - Title\n",
            "docs/decisions/README.md": "# Register\n\n- [0001](0001-a.md)\n- [0002](0002-b.md)\n",
        })
        self.assertEqual(findings(self.root, {"decisions": "docs/decisions/"})[0], [])
        write(self.root, {
            "docs/decisions/0004-d.md": DECISION.format(n="0004").replace("Decider: the owner\n", "") + "Superseded by [0009](0009-x.md)\n",
            "docs/decisions/0004-dup.md": DECISION.format(n="0004"),
            "docs/decisions/note.md": "# Not a record\n",
        })
        found, _, _ = findings(self.root, {"decisions": "docs/decisions/"})
        # 0004-d.md: no Decider, superseded by a missing record, and the link rule's broken link.
        self.assertEqual(sorted(found), ["docs/decisions/", "docs/decisions/0004-d.md", "docs/decisions/0004-d.md", "docs/decisions/0004-d.md", "docs/decisions/0004-dup.md", "docs/decisions/README.md", "docs/decisions/README.md", "docs/decisions/note.md"])
        texts = [m for _, m in doc_check.check(self.root, {"decisions": "docs/decisions/"}, today=TODAY)[0]]
        self.assertTrue(any("no record 0003" in t for t in texts))
        self.assertTrue(any("superseded by 0009" in t for t in texts))
        self.assertTrue(any("`Decider:`" in t for t in texts))

    def test_frozen_reports(self):
        write(self.root, {"docs/reports/2026-01-01-qa.md": "# QA\n", "docs/reports/README.md": "# Reports\n"})
        commit(self.root, date(2026, 1, 3))
        config = {"frozen": ["docs/reports/"]}
        self.assertEqual(findings(self.root, config)[0], [])
        write(self.root, {"docs/reports/2026-01-01-qa.md": "# QA\n\nLate edit.\n", "docs/reports/undated.md": "# X\n"})
        commit(self.root, date(2026, 2, 1))
        found, _, _ = findings(self.root, config)
        self.assertEqual(sorted(found), ["docs/reports/2026-01-01-qa.md", "docs/reports/undated.md"])
        found, _, _ = findings(self.root, {**config, "frozen_ok": ["docs/reports/2026-01-01-qa.md"]})
        self.assertEqual(found, ["docs/reports/undated.md"])

    def test_changelog_follows_state_changes(self):
        config = {"state": ["docs/handbook/"], "decisions": "docs/decisions/", "changelog": "docs/changelog.md"}
        write(self.root, {"docs/handbook/apps.md": STATE_PAGE, "docs/changelog.md": "# Changelog\n\n- 2026-11-01: start\n",
                          "docs/decisions/README.md": "# Register\n"})
        commit(self.root, date(2026, 11, 1))
        write(self.root, {"docs/handbook/apps.md": STATE_PAGE + "More.\n"})
        commit(self.root, date(2026, 11, 2))
        found, _, _ = findings(self.root, config)
        self.assertEqual(found, ["docs/changelog.md"])
        write(self.root, {"docs/handbook/apps.md": STATE_PAGE + "Even more.\n", "docs/changelog.md": "# Changelog\n\n- 2026-11-01: start\n- 2026-11-02: apps page\n"})
        commit(self.root, date(2026, 11, 3))
        self.assertEqual(findings(self.root, config)[0], [])
        # The staged set, for a pre-commit hook.
        write(self.root, {"docs/handbook/apps.md": STATE_PAGE + "Staged.\n"})
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True, env=GIT_ENV)
        self.assertEqual(findings(self.root, config, staged=True)[0], ["docs/changelog.md"])
        self.assertEqual(findings(self.root, config)[0], [])

    def test_changelog_decision_lines_name_their_record(self):
        write(self.root, {"docs/changelog.md": "# Changelog\n\n- 2026-11-02: the owner decided on pricing\n- 2026-11-03: decided (ADR 0002)\n- 2026-11-04: decided, docs/decisions/0003-x.md\n",
                          "docs/decisions/README.md": "# Register\n"})
        found, _, _ = findings(self.root, {"changelog": "docs/changelog.md", "decisions": "docs/decisions/"})
        self.assertEqual(found, ["docs/changelog.md"])
        texts = [m for _, m in doc_check.check(self.root, {"reach": [], "changelog": "docs/changelog.md"}, today=TODAY)[0]]
        self.assertEqual([t[:6] for t in texts], ["line 3", "line 5"])  # without `decisions`, only ADR NNNN names a record

    def test_only_in(self):
        config = {"frozen": ["docs/reports/"], "decisions": "docs/decisions/", "changelog": "docs/changelog.md",
                  "only_in": [{"pattern": r"KVK \d{8}", "files": ["docs/handbook/legal.md"]}]}
        write(self.root, {
            "docs/handbook/legal.md": "KVK 12345678\n",
            "docs/reports/2026-01-01-audit.md": "KVK 12345678\n",
            "docs/decisions/0001-a.md": DECISION.format(n="0001") + "KVK 12345678\n", "docs/decisions/README.md": "- [0001](0001-a.md)\n",
            "docs/archive/old.md": "KVK 12345678\n",
            "docs/changelog.md": "- KVK 12345678 published\n",
        })
        self.assertEqual(findings(self.root, config)[0], [])
        write(self.root, {"README.md": "# Repo\n\nKVK 12345678\n"})
        found, _, _ = findings(self.root, config)
        self.assertEqual(found, ["README.md"])

    def test_reference_pages(self):
        write(self.root, {
            "docs/reference/mistral.md": REFERENCE.format(checked="2026-11-01"),
            "docs/reference/README.md": "# Reference\n\n- [Mistral](mistral.md)\n",
        })
        found, notices, triggers = findings(self.root, {"reference": "docs/reference/"})
        self.assertEqual((found, notices), ([], []))
        self.assertEqual(triggers, [("docs/reference/mistral.md", "re-check when Mistral announces a model")])
        write(self.root, {"docs/reference/mistral.md": REFERENCE.format(checked="2026-07-01")})
        found, notices, _ = findings(self.root, {"reference": "docs/reference/"})
        self.assertEqual(found, [])
        self.assertEqual(notices, [("docs/reference/mistral.md", "re-check due since 2026-10-01 (every 3 months, checked on 2026-07-01)")])
        write(self.root, {
            "docs/reference/stripe.md": "# Stripe\n\nChecked on: 2027-01-01\nRe-check: yearly\n",
            "docs/reference/apple.md": "# Apple\n\nChecked on: 2026-11-01\n",
        })
        found, _, _ = findings(self.root, {"reference": "docs/reference/"})
        self.assertEqual(sorted(found), ["docs/reference/README.md", "docs/reference/README.md", "docs/reference/apple.md", "docs/reference/stripe.md", "docs/reference/stripe.md"])

    def test_exit_codes_and_json(self):
        write(self.root, {
            "docs-check.toml": 'reference = "docs/reference/"\n',
            "AGENTS.md": "# Repo\n\n- `docs/reference/README.md`: facts from outside\n",
            "docs/reference/mistral.md": REFERENCE.format(checked="2020-01-01"),
            "docs/reference/README.md": "# Reference\n\n- [Mistral](mistral.md)\n",
        })
        run = subprocess.run([sys.executable, "-I", str(SCRIPT), "--root", str(self.root), "--format", "json"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 4, run.stderr)
        out = json.loads(run.stdout)
        self.assertTrue(out["ok"])
        self.assertEqual(out["findings"], [])
        self.assertEqual(len(out["notices"]), 1)
        self.assertEqual(out["triggers"][0]["file"], "docs/reference/mistral.md")
        run = subprocess.run([sys.executable, "-I", str(SCRIPT), "--root", str(self.root)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 4)
        self.assertIn("docs: 1 notice(s)", run.stdout)
        self.assertIn("docs: 1 re-check trigger(s)", run.stdout)
        write(self.root, {"docs/reference/mistral.md": REFERENCE.format(checked="2099-01-01")})
        run = subprocess.run([sys.executable, "-I", str(SCRIPT), "--root", str(self.root), "--format", "json"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertIn("in the future", run.stdout)
        write(self.root, {"docs/reference/mistral.md": REFERENCE.format(checked=date.today().isoformat())})
        run = subprocess.run([sys.executable, "-I", str(SCRIPT), "--root", str(self.root), "--format", "json"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertEqual(json.loads(run.stdout)["notices"], [])


if __name__ == "__main__":
    unittest.main()
