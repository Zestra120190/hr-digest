# HR Digest

`index.html` is a self-contained daily briefing on UK employment law, served publicly via
GitHub Pages from the `claude/pages` branch at the custom domain **digest.hrlar.co.uk**. Its
reader is Lara — non-technical, non-lawyer, on Windows. A scheduled cloud routine ("HR Digest
daily refresh") rewrites and pushes it every morning around 07:00 UK time.

Rules for any edit:

- The page must stay fully self-contained: all CSS/JS inline, no external requests (no web
  fonts — use the local-font stacks already in the CSS variables), and keep the
  `<meta name="robots" content="noindex">` tag.
- Never delete the `CNAME` file (`digest.hrlar.co.uk`) — it holds the custom domain; removing it
  breaks the live site. Only edit `index.html` on a refresh.
- Keep the design identity: warm briefing-paper style matching hrlar.co.uk (Lara's portfolio) —
  serif "The HR Digest" masthead, at-a-glance tiles, news + Employment Rights Act timeline in the
  main column, rates/deadlines/case-law/checklist rail. Two themes via the CSS variables: DARK is
  the primary match (near-black `#111010`, cream text `#F0E6D3`, old-gold accent `#D4874A`); LIGHT
  is a warm cream-paper counterpart (bg `#F6F1E7`, warm ink `#201B15`, bronze-gold accent
  `#A85D22`). Do not reintroduce the old petrol-teal palette. Preserve the existing colour tokens.
- Keep the masthead credit to the RIGHT of the title, inline on the same baseline: a `.credit`
  span reading "— made by Lara Pegg" where "Lara Pegg" links to https://hrlar.co.uk. Do not
  remove it.
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
