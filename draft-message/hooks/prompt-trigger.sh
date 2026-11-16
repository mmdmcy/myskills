#!/bin/sh
# Claude Code UserPromptSubmit hook. When the prompt looks like a request for a mail or message,
# add one line of context so the session loads the draft-message skill before writing.
# Install (per machine), in ~/.claude/settings.json:
#   "hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command",
#              "command": "sh ~/.claude/skills/draft-message/hooks/prompt-trigger.sh"}]}]}
prompt=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null) || exit 0
printf '%s' "$prompt" | grep -qiE '(^|[^a-z])(e-?mail|mail(tje|s)?|bericht(je|en)?|whatsapp|appje|teams|sms|draft|concept|reply|antwoord(en)?|reageer)([^a-z]|$)' || exit 0
echo "The prompt mentions a mail or message. Before writing any text that goes out in the user's name, load the draft-message skill (Skill tool: draft-message)."
