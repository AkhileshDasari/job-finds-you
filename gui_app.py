"""
Flask web GUI for job scraper.
Run: python gui_app.py
Then visit http://localhost:5000
"""
from flask import Flask, render_template, jsonify, request
import requests
import threading
from config import COMPANIES
from keywords import SEARCH_TERMS, is_relevant, classify_type, is_location_relevant
from scrapers.workday import fetch_workday_jobs, fetch_workday_job_description
from scrapers.json_apis import fetch_google_jobs, fetch_microsoft_jobs, fetch_apple_jobs, fetch_amazon_jobs
from scrapers.eightfold import fetch_eightfold_jobs
from scrapers.fallback import build_fallback_rows
from keywords import extract_stipend

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Global state for scraping
scraping_state = {
    "is_scraping": False,
    "results": [],
    "progress": "",
    "error": None
}


def scrape_company(company, session, with_salary=False):
    """Returns a list of row-dicts for one company."""
    method = company["method"]
    name = company["name"]

    if method == "workday":
        jobs = fetch_workday_jobs(company["tenant"], company["wd_host"], company["site"],
                                   SEARCH_TERMS, session=session)
        rows = []
        for j in jobs:
            if not is_relevant(j["title"]):
                continue
            if not is_location_relevant(j.get("location", "")):
                continue
            stipend = "Not specified"
            if with_salary and j.get("external_path"):
                desc = fetch_workday_job_description(company["tenant"], company["wd_host"],
                                                       company["site"], j["external_path"], session=session)
                stipend = extract_stipend(desc)
            rows.append({
                "Company": name, "Category": company["category"],
                "Role Title": j["title"], "Type": classify_type(j["title"]),
                "Location": j.get("location", "Not specified"),
                "Apply Link": j["link"], "Stipend / Salary": stipend,
                "Posted": j.get("posted", ""),
            })
        return rows

    if method in ("google", "microsoft", "apple", "amazon"):
        fetch_fn = {"google": fetch_google_jobs, "microsoft": fetch_microsoft_jobs,
                    "apple": fetch_apple_jobs, "amazon": fetch_amazon_jobs}[method]
        jobs = fetch_fn(SEARCH_TERMS, session=session)
        rows = []
        for j in jobs:
            if not is_relevant(j["title"]):
                continue
            if not is_location_relevant(j.get("location", "")):
                continue
            rows.append({
                "Company": name, "Category": company["category"],
                "Role Title": j["title"], "Type": classify_type(j["title"]),
                "Location": j.get("location", "Not specified"),
                "Apply Link": j["link"], "Stipend / Salary": "Not specified",
                "Posted": j.get("posted", ""),
            })
        return rows

    if method == "eightfold":
        jobs = fetch_eightfold_jobs(company["tenant"], company["domain"], SEARCH_TERMS, session=session)
        rows = []
        for j in jobs:
            if not is_relevant(j["title"]):
                continue
            if not is_location_relevant(j.get("location", "")):
                continue
            rows.append({
                "Company": name, "Category": company["category"],
                "Role Title": j["title"], "Type": classify_type(j["title"]),
                "Location": j.get("location", "Not specified"),
                "Apply Link": j["link"], "Stipend / Salary": "Not specified",
                "Posted": j.get("posted", ""),
            })
        return rows

    if method == "fallback":
        return build_fallback_rows(company["url"], SEARCH_TERMS)

    return []


def run_scraper(with_salary=False):
    """Run all scrapers and collect results."""
    try:
        scraping_state["is_scraping"] = True
        scraping_state["error"] = None
        scraping_state["results"] = []
        
        session = requests.Session()
        all_rows = []
        
        for i, company in enumerate(COMPANIES):
            scraping_state["progress"] = f"Scraping {company['name']} ({i+1}/{len(COMPANIES)})..."
            try:
                rows = scrape_company(company, session, with_salary)
                all_rows.extend(rows)
            except Exception as e:
                print(f"Error scraping {company['name']}: {e}")
                scraping_state["progress"] = f"Scraped {company['name']} (with errors)"
        
        scraping_state["results"] = all_rows
        scraping_state["progress"] = f"✓ Scraping complete! Found {len(all_rows)} jobs."
        
    except Exception as e:
        scraping_state["error"] = str(e)
        scraping_state["progress"] = "Error during scraping"
    finally:
        scraping_state["is_scraping"] = False


@app.route("/")
def index():
    """Main page with scraping button."""
    return render_template("index.html")


@app.route("/api/scrape", methods=["POST"])
def scrape():
    """Start scraping in background thread."""
    if scraping_state["is_scraping"]:
        return jsonify({"error": "Already scraping"}), 400
    
    with_salary = request.json.get("with_salary", False) if request.json else False
    
    # Run scraper in background
    thread = threading.Thread(target=run_scraper, args=(with_salary,))
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "Scraping started"})


@app.route("/api/status")
def status():
    """Get current scraping status."""
    return jsonify({
        "is_scraping": scraping_state["is_scraping"],
        "progress": scraping_state["progress"],
        "error": scraping_state["error"],
        "result_count": len(scraping_state["results"])
    })


@app.route("/api/results")
def results():
    """Get all results."""
    return jsonify({
        "results": scraping_state["results"],
        "total": len(scraping_state["results"])
    })


@app.route("/api/results/<int:page>")
def results_paginated(page):
    """Get paginated results (10 per page)."""
    per_page = 10
    start = page * per_page
    end = start + per_page
    
    return jsonify({
        "results": scraping_state["results"][start:end],
        "total": len(scraping_state["results"]),
        "page": page,
        "pages": (len(scraping_state["results"]) + per_page - 1) // per_page
    })


if __name__ == "__main__":
    print("\n🚀 Job Scraper GUI starting...")
    print("📱 Open browser to http://localhost:5000")
    app.run(debug=True, port=5000)
