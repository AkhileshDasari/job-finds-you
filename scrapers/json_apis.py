"""
Best-effort scrapers for Google, Microsoft, Apple, and Amazon.

These call the same internal JSON endpoints each company's own careers
search box calls. They are NOT official/documented public APIs, so:
  - They can change or start blocking automated requests at any time.
  - Every function is wrapped so a failure here prints a warning and
    returns an empty list instead of crashing the whole run.
  - If a function suddenly returns 0 results, open the company's careers
    search page in a browser, open DevTools -> Network -> XHR, search for
    something, find the new request URL/response shape, and update the
    matching function below.
"""
import time
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-scraper/1.0)"}


def fetch_google_jobs(search_terms, session=None, delay=0.3):
    session = session or requests.Session()
    results = {}
    for term in search_terms:
        page = 1
        while page <= 5:
            try:
                resp = session.get(
                    "https://careers.google.com/api/v3/search/",
                    params={"q": term, "page": page},
                    headers=HEADERS, timeout=20,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                print(f"    [warn] Google careers request failed (term='{term}'): {exc}")
                break

            jobs = data.get("jobs") or []
            if not jobs:
                break
            for j in jobs:
                title = j.get("title", "")
                job_id = j.get("id") or j.get("job_id") or ""
                link = f"https://www.google.com/about/careers/applications/jobs/results/{job_id}" if job_id else ""
                loc = str(j.get("locations", ""))
                results[link or title] = {"title": title, "link": link, "posted": j.get("created", ""), "location": loc}

            if not data.get("has_more"):
                break
            page += 1
            time.sleep(delay)
    return list(results.values())


def fetch_microsoft_jobs(search_terms, session=None, delay=0.3):
    session = session or requests.Session()
    results = {}
    for term in search_terms:
        page = 1
        while page <= 5:
            try:
                resp = session.get(
                    "https://gcsservices.careers.microsoft.com/search/api/v1/search",
                    params={"q": term, "l": "en_us", "pg": page, "pgSz": 20, "o": "Relevance"},
                    headers=HEADERS, timeout=20,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                print(f"    [warn] Microsoft careers request failed (term='{term}'): {exc}")
                break

            result = (data.get("operationResult") or {}).get("result") or {}
            jobs = result.get("jobs") or []
            if not jobs:
                break
            for j in jobs:
                title = j.get("title", "")
                job_id = j.get("jobId", "")
                link = f"https://jobs.careers.microsoft.com/global/en/job/{job_id}" if job_id else ""
                loc = str(j.get("properties", {}).get("locations", ""))
                results[link or title] = {"title": title, "link": link, "posted": j.get("postingDate", ""), "location": loc}

            total = result.get("totalJobs", 0)
            if page * 20 >= total:
                break
            page += 1
            time.sleep(delay)
    return list(results.values())


def fetch_apple_jobs(search_terms, session=None, delay=0.3):
    session = session or requests.Session()
    results = {}
    for term in search_terms:
        try:
            resp = session.get(
                "https://jobs.apple.com/api/role/search",
                params={"search": term, "sort": "newest"},
                headers=HEADERS, timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            print(f"    [warn] Apple jobs request failed (term='{term}'): {exc}")
            continue

        for j in data.get("searchResults") or []:
            title = j.get("postingTitle", "")
            pos_id = j.get("positionId", "")
            link = f"https://jobs.apple.com/en-us/details/{pos_id}" if pos_id else ""
            loc = str(j.get("locations", j.get("locationString", "")))
            results[link or title] = {"title": title, "link": link, "posted": j.get("postDateInGMT", ""), "location": loc}
        time.sleep(delay)
    return list(results.values())


def fetch_amazon_jobs(search_terms, session=None, delay=0.3):
    session = session or requests.Session()
    results = {}
    for term in search_terms:
        offset = 0
        while offset < 100:
            try:
                resp = session.get(
                    "https://www.amazon.jobs/en/search.json",
                    params={"base_query": term, "offset": offset, "result_limit": 20, "sort": "recent"},
                    headers=HEADERS, timeout=20,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                print(f"    [warn] Amazon jobs request failed (term='{term}'): {exc}")
                break

            jobs = data.get("jobs") or []
            if not jobs:
                break
            for j in jobs:
                title = j.get("title", "")
                path = j.get("job_path", "")
                link = f"https://www.amazon.jobs{path}" if path else ""
                loc = f"{j.get('city', '')}, {j.get('country_code', '')}" if j.get('city') else j.get('location', '')
                results[link or title] = {"title": title, "link": link, "posted": j.get("posted_date", ""), "location": loc}

            offset += 20
            if offset >= data.get("hits", 0):
                break
            time.sleep(delay)
    return list(results.values())
