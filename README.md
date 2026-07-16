# MNC Internship / Fresher IT Job Scraper

Pulls entry-level, internship, and fresher (0–2 yrs) IT roles from 20 major
MNCs into a single CSV + Excel file.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

Output lands in `./output/jobs_<date>.csv` and `.xlsx`.

Optional: `python main.py --with-salary` also opens each Workday job listing
to scan its description for stipend/salary text (slower, only applies to
Adobe/Intel/NVIDIA/Salesforce).

## What you actually get, by company

This is split into three tiers, by how scrapeable each company's career site is:

### Tier 1 — Real scrape, reliable (Workday-hosted)
**Adobe, Intel, NVIDIA, Salesforce**
These run on Workday, which exposes a stable JSON search API. The script
queries it directly and returns real, current listings.

### Tier 2 — Real scrape, best-effort (internal/unofficial JSON APIs)
**Google, Microsoft, Apple, Amazon**
These call the same internal endpoint each company's own search box uses.
It's not an official public API, so it can change without notice. If a
company suddenly returns 0 results, see "If a scraper breaks" below.

### Tier 3 — Manual-check links (no scrapeable API)
**Meta, Oracle, TCS, Infosys, Wipro, HCLTech, Accenture, Cognizant,
Capgemini, IBM, Deloitte, PwC**
These sites are login-gated (TCS iBegin), GraphQL-only (Meta), or fully
JS-rendered single-page apps with bot protection (Oracle ORC, Avature/
SuccessFactors-based portals used by most consulting firms). Rather than
hand you scraping code that silently returns nothing, the script generates
direct, keyword-pre-filled search links into each portal — these show up in
your sheet with `Type = "Manual check required"` so you can one click into
current listings yourself.

If you want true automation for any of these, the realistic next step is a
Selenium/Playwright script per site (each needs its own selectors and,
for TCS, a login flow) — happy to build one out for a specific company if
useful.

## How filtering works (`keywords.py`)

A role is kept only if its title:
1. Contains an entry-level signal (intern, graduate, fresher, entry level, trainee, campus, early career, junior, co-op, apprentice...)
2. Does NOT contain a seniority word (senior, staff, principal, director, manager, lead, architect...)
3. Contains an IT/tech signal (software, developer, engineer, data, cloud, analyst, QA, security...)

Edit `SEARCH_TERMS`, `ENTRY_SIGNALS`, `SENIORITY_BLOCKLIST`, or `IT_SIGNALS`
in `keywords.py` to widen or narrow this.

## If a Tier 2 scraper breaks

Company career sites change their frontend occasionally, which can change
the JSON shape these unofficial endpoints return. To fix:
1. Open the company's careers search page in a browser.
2. Open DevTools → Network → filter to XHR/Fetch, then run a search.
3. Find the request that returns job results, and compare its URL/response
   shape to the matching function in `scrapers/json_apis.py`.
4. Update the `params` and field names (e.g. `j.get("title")`) accordingly.

Each function is isolated in a try/except, so one company breaking won't
stop the others from running.

## Project structure

```
config.py             # company list + how to scrape each one
keywords.py            # search terms + entry-level/IT filtering + stipend regex
scrapers/
  workday.py            # generic Workday CXS API scraper (Tier 1)
  json_apis.py           # Google/Microsoft/Apple/Amazon best-effort scrapers (Tier 2)
  fallback.py             # search-link generator for Tier 3
main.py                # orchestrator + CSV/Excel export
```

## A note on respectful scraping

The script only hits each site's own search endpoint at a light pace (small
delay between paginated requests) — please don't remove the delays or run it
on a tight loop/cron against these sites. If you plan to run this regularly,
consider checking each site's `robots.txt` and terms of use.

./venv/bin/pip install -r job-scraper/requirements.txt
./venv/bin/python job-scraper/main.py
