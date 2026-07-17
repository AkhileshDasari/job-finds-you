"""
Generic scraper for Eightfold AI ATS portals.
"""
import time
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-scraper/1.0)"}


def fetch_eightfold_jobs(tenant, domain, search_terms, session=None, delay=0.3):
    session = session or requests.Session()
    results = {}
    for term in search_terms:
        offset = 0
        while offset < 100:
            try:
                # e.g., tenant='aexp', domain='aexp.com'
                url = f"https://{tenant}.eightfold.ai/api/apply/v2/jobs"
                resp = session.get(
                    url,
                    params={"domain": domain, "query": term, "start": offset, "num": 20},
                    headers=HEADERS, timeout=20,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                print(f"    [warn] Eightfold request failed ({tenant}): {exc}")
                break

            jobs = data.get("positions") or []
            if not jobs:
                break
            for j in jobs:
                title = j.get("name", "")
                job_id = j.get("id", "")
                link = f"https://{tenant}.eightfold.ai/careers?query={term}&pid={job_id}" if job_id else ""
                loc = j.get("location", "")
                posted = j.get("t_update", "") or j.get("t_create", "")
                if isinstance(posted, (int, float)):
                    if posted > 20000000000:
                        posted = posted / 1000
                    import datetime
                    try:
                        posted = datetime.datetime.fromtimestamp(posted).strftime("%Y-%m-%d")
                    except:
                        posted = str(posted)
                        
                results[link or title] = {"title": title, "link": link, "posted": str(posted), "location": loc}

            offset += 20
            if offset >= data.get("count", 0):
                break
            time.sleep(delay)
    return list(results.values())
