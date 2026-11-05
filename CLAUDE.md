# HR Digest

`index.html` is a self-contained daily briefing on UK employment law, served publicly via
GitHub Pages from the `claude/pages` branch at the custom domain **digest.hrlar.co.uk**. Its
reader is Lara — non-technical, non-lawyer, on Windows. A scheduled cloud routine ("HR Digest
daily refresh") rewrites and pushes it every morning at 06:03 UTC (06:03 UK time in winter,
07:03 in summer). HR professionals act on it, so accuracy beats coverage: a missing story is
better than a wrong one, and a stale date is a wrong one.

Rules for any edit:

- Verify, don't just carry forward. Before searching the news, check the official record: the
  GOV.UK Employment Rights Act timeline's change history, the department's open consultations
  and recent outcomes, Acas consultations and the latest EAT decisions (the routine prompt has
  the exact URLs). If the timeline has changed since the page was compiled, and every Monday
  regardless, re-check every Employment Rights Act date on the page against it. Where the page
  and the GOV.UK timeline disagree, GOV.UK wins.
- Cite what you read. Every priority entry carries a small `Source ↗` link
  (`<a class="src" target="_blank" rel="noopener">`) in its `.rag-head`, every news sentence ends
  with one, and every case name is a link (`<a class="cn">`) to the judgment. Each points at the
  page that confirms the item: a primary source (GOV.UK, legislation.gov.uk, Acas, ONS, a court
  or tribunal judgment) wherever one exists. Only cite a page you have opened and read; a search
  snippet or a search tool's summary is a lead, not a source. If nothing you can open confirms
  a fact, leave it out.
- The page must stay fully self-contained: all CSS/JS inline, no external requests (no web
  fonts — use the local-font stacks already in the CSS variables). The page is public and
  search-indexable — do NOT add a `robots noindex` tag.
- Never delete the `CNAME` file (`digest.hrlar.co.uk`) — it holds the custom domain; removing it
  breaks the live site. Only edit `index.html` on a refresh.
- Keep the design identity: warm briefing-paper style matching hrlar.co.uk (Lara's portfolio) —
  serif "The HR Digest" masthead, at-a-glance tiles, priority list + news + Employment Rights Act
  timeline in the main column, rates/deadlines/case-law/checklist rail. Two themes via the CSS
  variables: DARK is the primary match (near-black `#111010`, cream text `#F0E6D3`, old-gold
  accent `#D4874A`); LIGHT is a warm cream-paper counterpart (bg `#F6F1E7`, warm ink `#201B15`,
  bronze-gold accent `#A85D22`). Do not reintroduce the old petrol-teal palette. Preserve the
  existing colour tokens.
- Keep the masthead credit to the RIGHT of the title, inline on the same baseline: a `.credit`
  span reading "— made by Lara Pegg" where "Lara Pegg" links to https://hrlar.co.uk. Do not
  remove it.
- Keep it short: Lara finds long text hard going. The word limits below are hard limits and
  apply to carried-forward text too. When adding a fact, cut another rather than lengthening an
  entry. Keep the page under 2,500 words, excluding the sources.
- Before every push, run `python3 tools/check.py` from the repo root (add `--links` when the
  network allows; otherwise open any new link with WebFetch). It checks dates, expiry, limits,
  sources and the rules below. Fix every FAIL and re-run; never push a page that fails. Never
  edit `tools/` on a refresh.
- Priority list (RAG): the page's main action section, at the top of the main column ABOVE the
  news card. Every live obligation or upcoming change gets one entry rated Red (do now — in
  force, overdue or a live risk today), Amber (do soon — in force or due within roughly 3
  months, or needs preparation now) or Green (on the horizon — confirmed but monitor only).
  Order Red → Amber → Green, soonest deadline first within each band; max 8 entries, noting any
  overflow in one line of names and dates separated by `·`, no full sentences. Each entry
  carries, in this order: What it is (max 20 words) / Why it matters (max 25) / Do now (max 35)
  / Then later (max 15). "Do now" must be a concrete step Lara can take this week without a
  lawyer — never "seek advice" or "review your position" alone. Anything in the news card that
  needs action must also appear here. RAG colours must not clash with the rates
  `up`/`par`/`down` coding.
- Priority-list entry `data-id` values are stable identifiers derived from the underlying
  obligation, not the date. Carry entries forward between refreshes and re-rate them each day.
  Each `<li>` carries `data-off` (YYYY-MM-DD), the date it comes off: six months after the change
  took effect or the ruling was handed down. Where a date isn't firm yet, count six months from
  the end of the stated period (e.g. "March 2027" → 2027-09-30, "2027" → 2028-06-30) and
  correct it once confirmed. Delete an entry once its
  `data-off` has passed, assumed done (the page's JS also hides it on the day); otherwise only
  drop one once it is done, superseded or no longer relevant — never because it isn't new. When a
  slot frees up, the highest-risk item on the overflow line moves in. If something that came off
  gets a genuinely new trigger (e.g. enforcement starts), add a new entry with a new `data-id`
  and its own date.
- "What's moving right now": max 5 items, one sentence each (max 30 words, ending with its
  `Source ↗` link) plus a bold "Do:" action line (max 20 words). Each `<li>` carries `data-off`:
  six weeks after the item's date, or the day after its action deadline if that is sooner (the
  page's JS also hides it on the day). On a quiet day, never add a filler item: change the
  card's `.sub` line to "No major new developments since D Mon." and keep the real items until
  they come off. A quiet week is a conclusion from checking the official record, not a default.
- Employment Rights Act timeline: a graphic, not prose. The dotted rail (`#rail`) is drawn by the
  page's JS from the `#stops` list, so edit only `#stops`. Each stop has a date (`.when`, e.g.
  "1 Jan 2027", "Late 2026", "2027"), a status chip, a short heading and a `.tags` list: max 6
  tags of max 7 words each, no sentences. Stop classes drive the colours and the "Today" marker:
  `is-live` (in force, "In force" chip), `is-soon` (next, amber chip, with a `data-due` countdown
  where the date is firm) or none (further out, "Ahead" chip). Flip them as dates pass.
- Case law rail: appellate decisions (EAT, Court of Appeal, Supreme Court) or cases with major
  national coverage only — no routine first-instance tribunal outcomes, fact-specific awards or
  "employee wins £X" stories. Re-apply that bar to entries carried forward, not just new ones.
  Max 8 entries. Each case name links to the judgment, and each `<li>` carries `data-off` six
  months after the decision (or after the step reported, e.g. permission to appeal). Each
  entry gets a one-line practical takeaway (max 25 words) plus a
  `<p class="means">` sentence (max 30 words) led by a bold "What it could change:" saying what
  the ruling does to the legal position — new binding precedent, confirmation of what the law
  already was, or still open pending appeal. Say "nothing yet" honestly where that's the answer;
  never overstate a first-instance or under-appeal ruling as settled law.
- Statutory rates table: Rate / Now / Rise columns, Rise colour-coded vs the CPI uprating
  benchmark (classes `up` / `par` / `down`), with the CPI note underneath. The rates card and
  the NLW tile carry `data-stale-after`: the date the next rates take effect (now 2027-04-01);
  after it the page flags them "May be out of date". Each April, switch to the new rates once in
  force (NLW/NMW 1 April, SSP 6 April, SMP and family pay from the first Sunday in April),
  verified on GOV.UK, benchmark them against the previous September's CPI, and move
  `data-stale-after` on a year.
- Dates to diary: firm dates only, each with a `data-due` countdown. Drop passed ones (the
  page's JS also hides them). The Open consultations tile, this list and the overflow line must
  match the open employment consultations on GOV.UK and Acas, with closing dates.
- `data-compiled` on the `.wrap` div must be today's ISO date on every refresh — it drives the
  staleness warning banner (`#stale-note`). Update the visible masthead, "Brief compiled" and
  footer dates to match, in Europe/London time (double-check the weekday).
- Action checklist: a rolling tick-list of what Lara should be working on now, re-checked on
  every refresh — not a fixed list. At least one item per live priority-list entry, in the same
  order, then dated changes still to come (soonest first), then consultations last; max 10 items,
  cutting from the end of that order, each a short action with a one-line `.why` (max 10 words).
  Each `<li>` carries `data-off` (YYYY-MM-DD), the date it comes off, matching its priority entry
  where it has one: six months after the change took effect or the ruling was handed down; for
  the consultations item, the day after the last open closing date. Delete an item once its
  `data-off` has passed, assumed done, even if it is unticked (the page's JS also hides it on the
  day). Take an item off sooner if its priority entry is done, superseded or no longer relevant.
  If something that came off gets a genuinely new trigger (e.g. enforcement starts), add a new
  item with a new `data-id`.
- Checklist checkbox `data-id` values are stable identifiers (localStorage key
  `hr-digest-checklist`): never rename one or reuse a retired one, and derive new ones from the
  underlying obligation, not the date. Retired so far: holiday-audit, family-leave.
- Never invent developments: only include facts confirmed by a page you opened. The footer
  `<details class="sources">` lists every per-item source plus any other page actually used;
  drop links that no longer support anything on the page and never keep a dead link. General
  information, not legal advice.
