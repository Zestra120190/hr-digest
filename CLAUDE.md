# HR Digest

`index.html` is a self-contained daily briefing on UK employment law, served publicly via
GitHub Pages from the `claude/pages` branch. Its reader is Lara — non-technical, non-lawyer,
on Windows. A scheduled cloud routine ("HR Digest daily refresh") rewrites and pushes it every
morning around 07:00 UK time.

Rules for any edit:

- The page must stay fully self-contained: all CSS/JS inline, no external requests, and keep
  the `<meta name="robots" content="noindex">` tag.
- Keep the design identity: petrol-teal briefing-paper style, serif "The HR Digest" masthead,
  at-a-glance tiles, news + Employment Rights Act timeline in the main column, rates/deadlines/
  case-law/checklist rail, light and dark themes.
- "What's moving right now": max 5 items, one sentence each plus a bold "Do:" action line.
- Statutory rates table: Rate / Now / Rise columns, Rise colour-coded vs the CPI uprating
  benchmark (classes `up` / `par` / `down`), with the CPI note underneath.
- `data-compiled` on the `.wrap` div must be today's ISO date on every refresh — it drives the
  staleness warning banner (`#stale-note`). Update the visible masthead, "Brief compiled" and
  footer dates to match, in Europe/London time (double-check the weekday).
- Checklist checkbox `data-id` values are stable identifiers (localStorage key
  `hr-digest-checklist`): never rename existing ones — holiday-audit, rtw, harassment,
  probation, dp-complaints, union-access, family-leave, consultations.
- Never invent developments: only include facts confirmed by research, keep the footer source
  links pointing at pages actually used, and say "no major developments" honestly on quiet
  weeks. General information, not legal advice.
