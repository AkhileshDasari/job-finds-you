"""
Generic scraper for any company career site hosted on Workday
(*.myworkdayjobs.com). Workday exposes a consistent, unauthenticated JSON
search API at:

    POST https://{tenant}.{wd_host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs

This is the same endpoint the career site's own search box calls, so it's
a stable, reliable way to pull listings (no browser/Selenium needed).
"""
import time
import requests

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; job-scraper/1.0)",
}


def fetch_workday_jobs(tenant, wd_host, site, search_terms, session=None,
                        max_per_term=100, page_size=20, delay=0.3):
    """Returns a deduped list of {title, link, posted} dicts."""
    session = session or requests.Session()
    base_url = f"https://{tenant}.{wd_host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    results = {}

    for term in search_terms:
        offset = 0
        while offset < max_per_term:
            payload = {"appliedFacets": {}, "limit": page_size, "offset": offset, "searchText": term}
            try:
                resp = session.post(base_url, json=payload, headers=HEADERS, timeout=20)
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                print(f"    [warn] Workday request failed ({tenant}, term='{term}'): {exc}")
                break

            postings = data.get("jobPostings", [])
            if not postings:
                break

            for p in postings:
                title = (p.get("title") or "").strip()
                path = p.get("externalPath") or ""
                link = f"https://{tenant}.{wd_host}.myworkdayjobs.com/en-US/{site}{path}"
                results[link] = {
                    "title": title,
                    "link": link,
                    "posted": p.get("postedOn", ""),
                    "external_path": path,
                    "location": p.get("locationsText", ""),
                }

            offset += page_size
            total = data.get("total", 0)
            if offset >= total:
                break
            time.sleep(delay)

    return list(results.values())


def fetch_workday_job_description(tenant, wd_host, site, external_path, session=None):
    """Optional deep-fetch of a single job's full description (for stipend/salary extraction)."""
    session = session or requests.Session()
    url = f"https://{tenant}.{wd_host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}{external_path}"
    try:
        resp = session.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return data.get("jobPostingInfo", {}).get("jobDescription", "")
    except Exception:
        return ""
