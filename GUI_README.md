# Job Scraper GUI - Setup Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Running the GUI

```bash
python gui_app.py
```

Then open your browser to: **http://localhost:5000**

## Features

✅ **Simple Scraping Button** - One-click to start scraping all MNCs  
✅ **Real-time Progress** - Watch the status as each company is scraped  
✅ **Search & Filter** - Filter by company, role title, or location  
✅ **Direct Links** - Click "Apply" buttons to go directly to job listings  
✅ **Salary Extraction** (optional) - Extract salary info from Workday listings (slower)  
✅ **Responsive Design** - Works on desktop and mobile  

## How to Use

1. **Start Scraping**: Click "Start Scraping" button
2. **Optional**: Check "Extract salary info" for more details (slower)
3. **Wait**: Watch the progress bar as each company is scraped
4. **Search**: Use search box and category filters to narrow down results
5. **Apply**: Click "Apply" button on any job to visit the listing

## Original CLI

Still available via:
```bash
python main.py                    # Basic scraping
python main.py --with-salary      # Include salary info (slower)
python main.py --output-dir ./out # Custom output directory
```
