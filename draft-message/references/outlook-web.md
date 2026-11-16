# Putting a draft in Outlook web (the user's browser)

Loose keystrokes in Outlook web can archive a colleague's mail and open blank drafts. Everything
here is the safe route; the unsafe shortcuts are named so nobody rediscovers them.

## Never type blind

Outlook web treats loose keystrokes as shortcuts: `n` opens a new message, `e` archives the open
mail, `Delete` deletes it. A `find` ref of a recipient field is not proof that the field has focus.
So: no keyboard text into Outlook unless the previous action put the cursor in an input and the
screenshot shows it. Never press Return in a recipient field (it can pick the wrong suggestion).

## Make the draft with the compose deeplink

```
https://outlook.cloud.microsoft/mail/deeplink/compose?to=a@example.com;b@example.com&subject=...&body=...
```

- URL-encode subject and body; newline is `%0A`, a blank line `%0A%0A`.
- The `cc` parameter is ignored. Say so and let the user add cc himself.
- It is a new message, not a reply in the thread. If the mail answers a thread, put "RE: <subject>"
  in the subject and name the mail it answers in the first line.
- Open it in a new tab (with Claude in Chrome: `tabs_create_mcp`, then `navigate`). Outlook saves
  the draft itself after a few seconds; read the Drafts folder back before saying it is there.
- The default font is Segoe UI. When the folder has a house font (Aptos 12pt, say), wrap the body
  in a `<div style="font-family:Aptos,Calibri,sans-serif;font-size:12pt">` via JavaScript on the
  editor's `[contenteditable]`, after the deeplink has filled the body.

## Images (graphs) in the body

- Only a fresh compose window accepts uploads. A reopened draft silently refuses them. If images
  are needed, make the whole draft again via the deeplink and upload right after it has loaded.
- Upload through the hidden `input[type=file]` (with Claude in Chrome: `file_upload`). In the
  compose window there are several inputs; the one that places the image inline is the one near
  the editor (when this was written, the third input; the fourth attaches as a file). Verify with a screenshot: inline images show in the
  body, attachments show in the attachment bar.
- Uploaded images land at the cursor, usually above the signature. Move them to the end with
  JavaScript: find the image blocks (`img` ancestors that are direct children of the editor),
  append them after the signature in the intended order, keep a blank line between them. Check the
  DOM once more afterwards: a greedy ancestor match can remove a sibling image, which then has to
  be uploaded again.
- A screenshot of the finished body, scrolled to the bottom, is the proof. "I have added them" is
  not.

## Snippets of a dashboard or site as images

Render with a headless browser (Playwright), not with the user's browser:
- inject CSS that hides the controls (`details`, `summary`, buttons, period pickers, explanation
  blocks) and gives the element margin, then take an element screenshot;
- one image per message block, each with its own heading inside the image, so it survives being
  forwarded without the text;
- the image must show what the text claims and nothing that undercuts it unintentionally
  (a "visitors per day" chart that is flat next to a story about growth needs its own line of
  explanation, or stays out).

## Stray drafts

- Every closed compose tab saves one more copy in Drafts. After each attempt open Drafts and
  delete the copies by opening each one (click the item, check the subject and the first line,
  then the Discard/Delete control), never with the keyboard.
- Before telling the user the draft is ready, name the exact count: "one draft in Drafts, subject
  X, to A and B, four images at the bottom".

## When something goes wrong

Stop. Do not fix forwards. Report the exact state: which mails moved where, which drafts exist,
what the last action was. Propose numbered steps, one per line, and do them one at a time with a
screenshot after each. A moved mail goes back to its folder first, before anything new is started.
