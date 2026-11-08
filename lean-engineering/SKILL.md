---
name: lean-engineering
description: An engineering philosophy for designing, building, reviewing and refactoring any software (products, internal tools, client work). Use before planning a feature, when choosing between approaches or dependencies, when reviewing what was built, and before shipping. Fast, lean, KISS, Unix-style small parts that snap together like Lego, generic and reusable, secure by default, a seamless developer experience.
---

# Lean engineering

Build things an enterprise could adopt and a single person can understand.
When a choice is unclear, pick the option that is smaller, simpler, safer and
more general, and say why in one sentence.

## The rules

1. **Keep it simple (KISS).** The simplest design that fully solves the real
   problem wins. No speculative options, layers or abstractions. Delete
   before you add. If it needs a long explanation, it is too complicated.

2. **Do one thing well (Unix).** Small parts with one job, plain text or
   JSON in and out, composable from a shell. Every feature is a CLI command
   first (`--format json`, `--dry-run`, `--yes`), then the same thing in the
   GUI. A person, a script and an AI agent use the same interface.

3. **Lego bricks (modular).** A small core plus modules you can switch off
   or remove without breaking the rest. A module owns its commands, checks,
   timers and pages; nothing reaches into another module's internals. No
   two parts do the same job: before adding an agent, daemon, token or
   protocol, check whether an existing one already covers it, and extend
   that instead.

4. **Lean and fast.** Few dependencies: write small, well-specified parts
   in-house; use the operating system's own tools when they are proven;
   take libraries only for foundations and cryptography. No background
   process that does not earn its memory. Measure (RAM, CPU, disk, power,
   latency) instead of guessing, and write the numbers down. Contact an
   outside service only when a local fact says something changed (a new
   commit, a new file), never on a short fixed timer; keep its last answer.

5. **Generic, not personal.** Product code never contains one owner's
   machines, names, addresses, prices or paths. Those live in that owner's
   private config or fleet repository, which the product reads. Ask: would
   another company be able to use this unchanged?

6. **Secure by default.** Least privilege; keys made on the device that
   uses them and never moved; no shared secret that unlocks everything;
   nothing listening publicly that does not have to; validate every input
   before it reaches a shell; never print secrets. Prefer one well-known,
   audited channel (SSH, WireGuard, OIDC) over a home-made one.

7. **Never destructive.** Changes add; replaced files are kept as
   `.bak-DATE`; removals become commented-out or archived. Show the plan
   before changing anything, and make every step safe to run twice.

8. **Official and clean on every platform.** Use each platform's own,
   documented mechanism (systemd on Linux, launchd on macOS, Task Scheduler
   and OpenSSH Server on Windows, WSL's own settings). Keep Linux and
   Windows clearly apart: a command says which shell it runs in, and
   PowerShell is passed encoded, never through nested quoting.

9. **Seamless developer experience.** No silent caps, truncation or
   timeouts that ignore what was asked; errors say what happened and the
   exact next command. Names over addresses: nobody should need to know an
   SSH alias or an IP to reach their own device. If doing it by hand feels
   easier than using the tool, the tool is missing a feature: add it.

10. **Organized and documented.** One decision record per real decision
    (context, decision, consequences). The written state (handbook, runbook)
    is updated in the same change. Clear names, consistent idioms, code that
    reads like its surroundings.

11. **Features, not one-offs.** A check or chore done by hand once (which
    versions run where, what an advisory touches, whether two devices
    match, what a network exposes, which skills an agent has) becomes a
    read-only command the same day and, where it should run on its own, an
    Attention item or a timer. Every version an advisory could name is one
    command away for every device, containers included; a vendor's "we were
    hit" is answered by running it, not by searching by hand. The fleet's
    own tools update themselves on a timer; a person is told, not asked,
    for routine builds. This is for checks that come back. A one-time job
    (one handover, one migration) stays a one-off script or note, or makes
    an existing command say more; it does not become a new command.

## Before building

- What problem, for whom, and what is the smallest thing that solves it?
- Does something we already have do this, or almost, even from the other
  side? Extend it, or make its output say more; never build a second part
  that compares the same things the other way round (2026-11-03: a
  receiver's checklist rebuilt what the receipt already judged).
- Write the answer down before building or briefing anyone: "extends X"
  or "searched for Y, nothing exists". The same before calling a finding
  new: check what the system already records.
- Is the request the best route to what the person wants? If a cheaper,
  safer or already-decided route exists, say so first, with a
  recommendation.
- Which module does it belong to, and can that module be switched off?
- What does it cost to run (memory, CPU, processes, network, money)?
- What is the attack surface, and who could misuse it?
- Is anything in it specific to one person or machine?

## Before shipping

- Tests for the logic, including refused inputs; the real path tried end to
  end (QA), not just compiled.
- Tests never reach the real world: a desktop notification, a phone push,
  a network call or a device goes through a variable the test replaces.
- CLI and GUI both done, `--format json` works, help text and examples.
- Measured footprint where it runs all the time.
- Docs and decision record updated; nothing personal in product code.
- Commits as the owner, without AI attribution lines.

## Reviewing what exists

Look for: two parts doing the same job, features nobody uses, background
processes that could be on demand, shared secrets, hand-made protocols
where a standard one exists, owner-specific data in product code, silent
limits, and places where using the tool is harder than doing it by hand.
Report findings ranked by impact, with the smallest fix for each.
