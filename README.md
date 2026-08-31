# internship-alert-bot
# 🤖 Internship Alert Bot

Welcome! This is a Discord bot designed to automatically track, scrape, and post real-time internship opportunities to keep members of **StackHacks** ahead of the application curve. 

Built with ❤️ (def not vibe coded) by **Ryan Tsui** (Director of Professional Development).

---

## 📌 Features

* **Automated Job Scraping:** Continuously checks for new internship postings across target job boards and repositories.
* **Instant Discord Alerts:** Sends rich embedded notifications directly to designated Discord channels as soon as new listings are found.
* **Duplicate Prevention:** Tracks previously seen listings (`seen_jobs.json`) to prevent spamming duplicate alerts.
* **Custom Filters:** Configurable search parameters for specific roles, locations, or technical stacks.

---

## 🛠️ Tech Stack & Dependencies

* **Language:** Python 3.x
* **Scraper:** BeautifulSoup4 / Requests / Selenium
* **Discord Integration:** `discord.py` / Webhooks
* **Storage:** JSON key-value tracking (`seen_jobs.json`)

---

## 🚀 Quick Start & Setup

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your machine.

### 2. Installation
Clone the repository and install the required dependencies:

```bash
git clone [https://github.com/rtsui335/internship-alert-bot.git](https://github.com/rtsui335/internship-alert-bot.git)
cd internship-alert-bot
pip install -r requirements.txt

-Ryan Tsui
