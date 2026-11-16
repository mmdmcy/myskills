---
name: draft-message
description: Write an email, WhatsApp, Teams or other message in the user's name, in Dutch or English, for work or private use. Use whenever the user asks for a mail, message, reply, draft, concept, WhatsApp, text to a colleague or supplier, or to put a draft in Outlook. It forces the checks that drafts fail on, such as wrong channel, asking the recipient what they cannot know, the wrong voice for the sender's role, invented facts, unchecked numbers and graphs, and announcing the next step. Also covers putting the draft in Outlook web safely (deeplink, images, no keyboard).
---

# Draft a message in the user's name

A message goes out under the user's name, to a real person, and the user is judged on it.
One illogical line costs more than ten good ones. Do these checks before writing, and show the
checks after the draft.

## The sender's own voice

How the user writes (the words they use, what they capitalise, their greeting and sign-off,
their house font) is personal and is not in this skill. When the user's agent rules or the
folder's rules name a voice file for messages, read it before writing; where it differs from
the general rules below, the voice file wins. Without one, write plainly and ask nothing about
style.

## Before writing

1. **Channel.** Mail, WhatsApp, Teams, SMS. WhatsApp and Teams: short, a first-name greeting
   ("Hoi <naam>", "Hi <name>"), no signature block, no phone number, never "call me anytime"
   ("bel me gerust": the recipient already has the number, and you are already in a chat).
   Mail: a greeting and one sign-off in the form the folder uses.
2. **Recipient.** Who they are, what they already know, what they can answer. Never ask what we
   can see ourselves (our own systems, our own mailbox, our own site). Never ask what they
   cannot know (what another supplier did, who manages something outside their job). Do not
   address one person at a shared or sales address unless the user says so.
3. **Sender.** The user's role and mandate. No permission questions for things inside that
   mandate, no apologies for response time, no lessons or "for the future" to suppliers,
   nothing pushed to a third party that we do ourselves. Read the folder's rules on mails.
4. **Facts.** Every statement traces to a mail, a document, a screen, or the user's words in
   this conversation. Before writing "no reply yet" or "we never heard back", look in Sent
   Items and the folder's timeline. An assumption does not go into the message as a hedge
   ("maybe", "misschien", "or not?"); it goes to the user as a question before the draft, or it
   is left out. State what we know as fact: "In the dashboard I see ...".
5. **Purpose.** One sentence: what should the recipient do after reading. If the message has
   no such sentence, it is not ready.

## Writing

- Short. A chat message (WhatsApp, Teams) is two to four sentences: the answer, at most one
  reason, nothing the recipient did not ask. The explanation goes in the logbook or handbook,
  not in the chat. A mail is at most three short paragraphs.
- No semicolons. Start a new sentence instead.
- **Chat reads like typed on a phone, not like a letter.** In WhatsApp and Teams: a colon only
  to introduce what follows ("two more things: ..."), never before a list of examples; no
  "for example X, Y or Z" enumerations with perfect commas; a sentence may start with "and" or
  "but"; a question mark does the asking; no "Thanks," openers. Names, brands and capitals the
  way the user types them (their voice file says how). Mail is a notch neater, still no letter.
- One subject per paragraph. More than three questions: a bulleted list.
- Concrete: which product, which order, which date, which amount, which person.
- Natural language in the recipient's language. Dutch is written as a Dutch colleague would
  write it, not translated from English ("Zou je je reactie naar ons allebei willen sturen?",
  not "stuur alles naar ons allebei").
- Confident, not uncertain, not demanding. No instructions on how they should answer ("a few
  lines per point is enough" is rude). No questions whose only answer is "of course" ("tuurlijk
  mag dat").
- No invented follow-ups ("I'll take that up with X this week" only if that is agreed).
- No passwords, codes or keys, unless the user explicitly says this channel is fine.
- Read it once as the recipient: does every name, product and date mean something to them?

## Mails with numbers, graphs or results (for a boss, a colleague, a client)

A mail like this is where drafts go wrong most: one number or graph that is wrong, or that
makes the user look bad, undoes the rest.

- **Recompute every factor and percentage from the raw data before the draft is shown**, and write
  the arithmetic under the draft (a "+26%" can turn out to be a 6-day week against a 7-day week,
  "+8% per day" being the truth). Compare equal periods only. Round the way the recipient reads:
  "almost 3 times", "+33%", not "2.91x".
- **Say what each number is**, in the recipient's words: "visitors from Google" (Search Console
  clicks), not "clicks"; "measured for visitors who accept cookies" when it is a consent-based
  analytics tool; "according to the ticket system" when it is. The source and date of every
  number go under the draft.
- **A graph must show what it promises.** An analytics tool's "revenue" is not revenue when it
  only counts consenting visitors or shops that started measuring half-way. Visitors on site are
  not a website number. Two series that are not comparable get no "better" verdict. If the graph
  needs a disclaimer longer than its title, leave it out.
- **Separate the user's work from others' work** by what actually separates them: channel (organic
  versus paid), site (sites without campaigns), origin (UTM tags), time (the weeks before the ads
  and before a holiday). Name the interaction (brand searches after ads, brand campaigns catching
  organic clicks) in the mail itself, once, as an interpretation, not as a fact. The graphs show
  the user's part; the other party's part is text or a second graph, never the hero.
- **Highlights with factors, no list of raw numbers.** The first paragraph is the one sentence the
  boss repeats to others. Then the proof per site or per week, then the rest. Peak days and "it
  did not fall back after the holiday" are highlights, say them.
- **The reader gets the numbers in the mail**, not a link to an internal page as bait. A link may
  follow the numbers, for the full table.
- **Internal setbacks stay out** (a rejected appeal, a tool that failed) unless the user wants them
  in. Ask once if unsure.
- **What the user states is stated.** A fact the user gave ("there are no signs", "the front desk
  does not answer") goes in without "as far as I know". A fact nobody has recorded becomes a
  question in the mail ("who gives the front desk that instruction?"), not a guess.
- **Do, don't announce.** "The numbers are in the ticket system" is not a line for a mail when
  they are not in the user's overview yet: fetch them, put them in, then write that they are there.
- **Images in the mail:** one per highlight, in the order of the text, at the end after the text and
  signature, each self-explaining (its own title in the image, controls and "view as table" links
  hidden). See `references/outlook-web.md` for how to get them into Outlook.

## Process

- One message at a time, in the order the user chooses. Never announce which draft comes next.
- Show the draft as plain paragraphs: no Markdown blockquote, no code block, no bullets other
  than the message's own. The user copies it straight into Outlook or WhatsApp.
- Under the draft, three short lines: the channel; what the recipient knows or can answer
  (why each question is fair); the source of each fact that is not common knowledge.
- Never send. Put it in Outlook as a concept only when the user asks, in one tab, and read it
  back from the screen before saying it is there. Outlook web in the user's browser has traps
  (keyboard shortcuts, cc dropped by the deeplink, reopened drafts refuse images, closed tabs leave
  copies): follow `references/outlook-web.md` step by step.
- When the user says the result is wrong or asks what is going on: stop, state the exact state in
  three lines, propose numbered steps, do one, show a screenshot, continue. No fixing forwards.
- The user decides on sending and on when the next draft comes. After "go", the next message is
  the draft, not a plan for it.
- When the user has sent it, record that where the folder records sent messages (its timeline or
  logbook), with the time from Sent Items, not from memory.

## Hook

`hooks/prompt-trigger.sh` is a Claude Code `UserPromptSubmit` hook that reminds a session to load
this skill when a prompt mentions a mail or message; the install line is in the script. A skill
that is never loaded checks nothing.
