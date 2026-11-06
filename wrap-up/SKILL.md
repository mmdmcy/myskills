---
name: wrap-up
description: Close a long Claude Code session without losing its context. Use when the user says wrap up, close this session, write things down, hand off, or wants to start a fresh conversation in this folder. Writes the handoff where the folder keeps its state, turns the user's corrections into rules, saves a project memory, lists what is unpushed or waiting on the user, and gives the one line that starts the next session.
---

# Wrap up a session

The conversation is about to be closed. Everything the next session needs must be in files
by the end of this turn. Do only this; start no new work and ask no questions (state an
assumption instead).

## 1. Take stock, from the conversation itself

Write down, in this order:

- what the user asked, in order, and what was delivered and verified (say what was checked
  and what was not);
- decisions made, and who made them (the user, a colleague, you);
- what is unfinished, and the exact next step for each item;
- what waits on the user: drafts to send, pushes to approve, questions a colleague must answer,
  dates to chase;
- facts that live only in this conversation: names and who is who, numbers, dates, paths,
  account names, things the user told you that are in no file yet;
- corrections the user made to your work, each in one line, as a rule for next time.

Facts come with a source and a date (a mail, a document, a screen, the user's words). What you
inferred stays marked as inferred.

## 2. Check the state of the work

- `git fetch -q; git status -sb; git log --oneline @{u}..` in every repository you touched.
  List uncommitted files and unpushed commits. Commit your own finished files and push them
  after you have double-checked and QA'd them, as the folder's rules allow (when the user has said pushing is fine after
  checks). Leave nothing unpushed only for want of the user's word.
- Scripts or exports in your scratchpad that the next session needs: copy them into the
  project in the place its conventions give them.
- Anything you left in a half state (a draft open in Outlook, a service you changed, a file
  renamed): name it.

## 3. Write the handoff where the folder keeps its state

Follow the folder's `AGENTS.md` (a folder that still has only a `CLAUDE.md`: that file): a
logbook, a timeline, a project sheet, an open-items file, a "where things stand" section. Update
those. If the folder has no such place, add a dated section `## Where things stand (YYYY-MM-DD)`
to its `AGENTS.md`, or create `HANDOFF.md` when there is none. Open items go to the owner's one
open list, not into the handoff.

The corrections from step 1 become one-line rules in the folder's `AGENTS.md` (its rules
section), so the next session does not repeat the mistake. A new rules file is always
`AGENTS.md`, the name every coding agent reads. Keep the file's language and style.

A correction about a kind of work that has its own skill (a message or mail: `draft-message`;
code: `lean-engineering`) goes into that skill, in the same commit as the handoff, because the
skill is what the next session reads before doing that work on any machine. The folder's
`AGENTS.md` keeps only the folder-specific version (names, paths, house style).

If the folder lives on two machines without syncing and its rules say to copy, copy the changed
documents to the other machine (for example with the fleet tool's send command). Do not copy secrets.

## 4. Save the memory

In the auto memory directory for this project (the path is in the system prompt) write
`handoff-YYYY-MM-DD-<topic>.md` with `type: project`: the compact version of step 1 (under 40
lines), with absolute dates and `[[links]]` to related memories. Add it to `MEMORY.md`. Each
correction the user made that is about how you work becomes a `type: feedback` memory with
**Why** and **How to apply**, or extends an existing one.

## 5. Report

Reply with these headings and nothing else:

- **Done** (verified) and **Done, not verified**
- **Open** (with the next step each)
- **Waiting on you**
- **Where it is written** (file paths)
- **Start the next session with:** one line the user can paste into a new session in this
  directory, of the form "Read AGENTS.md and <handoff file>, then continue with <next step>."

Never say the session is wrapped up while a file in step 3 or 4 is unwritten.
