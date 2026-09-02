An automated monitoring and notification system designed to track, scrape, and dispatch real-time internship opportunities to keep **StackHacks** members ahead of the application process.

---

## Key Features

* **Automated Web Scraping:** Continuously monitors target job boards and career repositories for new internship postings.
* **Instant Discord Alerts:** Sends formatted, rich embed notifications directly to designated channels upon detecting new listings.
* **Deduplication Engine:** Leverages persistent state tracking (`seen_jobs.json`) to prevent duplicate alerts and redundant notifications.
* **Configurable Filtering:** Tailor search criteria based on specific role titles, locations, technologies, or keywords.

---

## Tech Stack

* **Core:** Python 3.8+
* **Scraping & Parsing:** BeautifulSoup4, Requests, Selenium
* **Integration:** `discord.py`, Webhooks
* **Storage:** JSON File-based Key-Value Store

---

## Getting Started

### Prerequisites

Ensure you have Python 3.8 or higher installed on your environment.

```bash
python --version
