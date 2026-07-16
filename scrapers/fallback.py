"""
Fallback for companies with no usable scrapeable API: login-gated portals
(TCS iBegin), GraphQL-only sites (Meta), or fully JS-rendered SPAs that need
a real browser session (Oracle ORC, Accenture/Cognizant/Deloitte/PwC/IBM
career platforms, etc).

Rather than ship scraping code that silently returns nothing (or breaks)
against these, we generate direct, keyword-pre-filled search links so the
person can one-click check current openings themselves. These rows are
clearly labeled "Manual check required" in the output sheet.
"""


def build_fallback_rows(url_template, search_terms):
    rows = []
    seen_links = set()
    for term in search_terms:
        if "{query}" in url_template:
            link = url_template.format(query=term.replace(" ", "+"))
        else:
            link = url_template
        if link in seen_links:
            continue
        seen_links.add(link)
        rows.append({
            "title": f"Manual check: search \"{term}\" openings",
            "link": link,
            "posted": "",
            "location": "N/A",
        })
    return rows
