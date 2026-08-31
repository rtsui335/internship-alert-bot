import hashlib
import json
import os
import re
from pathlib import Path

import requests


SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "SimplifyJobs/Summer2027-Internships/dev/README.md"
)

SEEN_FILE = Path("seen_jobs.json")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Roles we're interested in
KEYWORDS = [
    "software",
    "software engineer",
    "software engineering",
    "developer",
    "full stack",
    "fullstack",
    "backend",
    "back end",
    "frontend",
    "front end",
    "data engineer",
    "data science",
    "machine learning",
    "artificial intelligence",
    " ai ",
    " ml ",
]


def get_readme():
    response = requests.get(SOURCE_URL, timeout=30)
    response.raise_for_status()
    return response.text


def clean_markdown(text):
    # Convert markdown links: [Google](url) -> Google
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove basic HTML
    text = re.sub(r"<[^>]+>", "", text)

    return text.strip()


def extract_link(text):
    match = re.search(r'href="([^"]+)"', text)

    if match:
        return match.group(1)

    match = re.search(r"\]\((https?://[^)]+)\)", text)

    if match:
        return match.group(1)

    return None


def parse_jobs(readme):
    jobs = []

    for line in readme.splitlines():

        # Internship rows are markdown/HTML table rows
        if not line.startswith("|"):
            continue

        columns = [column.strip() for column in line.split("|")[1:-1]]

        if len(columns) < 4:
            continue

        company_raw = columns[0]
        role_raw = columns[1]
        location_raw = columns[2]
        application_raw = columns[3]

        company = clean_markdown(company_raw)
        role = clean_markdown(role_raw)
        location = clean_markdown(location_raw)

        # Ignore table headers
        if company.lower() == "company":
            continue

        if "---" in company:
            continue

        link = extract_link(application_raw)

        # Rows without an application link aren't useful for our alerts
        if not link:
            continue

        jobs.append(
            {
                "company": company,
                "role": role,
                "location": location,
                "link": link,
            }
        )

    return jobs


def is_relevant(job):
    text = f" {job['role'].lower()} "

    return any(keyword in text for keyword in KEYWORDS)


def job_id(job):
    # Application URL gives us a stable identifier
    return hashlib.sha256(
        job["link"].encode("utf-8")
    ).hexdigest()


def load_seen():
    if not SEEN_FILE.exists():
        return set()

    with open(SEEN_FILE, "r") as file:
        return set(json.load(file))


def save_seen(seen):
    with open(SEEN_FILE, "w") as file:
        json.dump(sorted(seen), file, indent=2)


def send_discord(job):
    if not WEBHOOK_URL:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not set.")

    payload = {
        "embeds": [
            {
                "title": "🚨 New Summer 2027 Internship",
                "description": f"**{job['role']}**",
                "url": job["link"],
                "fields": [
                    {
                        "name": "🏢 Company",
                        "value": job["company"],
                        "inline": True,
                    },
                    {
                        "name": "📍 Location",
                        "value": job["location"],
                        "inline": True,
                    },
                    {
                        "name": "🔗 Application",
                        "value": f"[Apply Here]({job['link']})",
                        "inline": False,
                    },
                ],
                "footer": {
                    "text": "SimplifyJobs Summer 2027 Internship Monitor"
                },
            }
        ]
    }

    response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
    response.raise_for_status()


def main():
    print("Checking SimplifyJobs...")

    readme = get_readme()
    jobs = parse_jobs(readme)

    relevant_jobs = [job for job in jobs if is_relevant(job)]

    print(f"Found {len(jobs)} total internships.")
    print(f"Found {len(relevant_jobs)} relevant CS internships.")

    seen = load_seen()

    # First run:
    # mark everything currently listed as seen.
    # This prevents 100+ Discord notifications.
    if not seen:
        seen = {job_id(job) for job in relevant_jobs}
        save_seen(seen)

        print("First run complete.")
        print(f"Initialized database with {len(seen)} existing jobs.")
        print("No Discord notifications sent.")
        return

    new_jobs = [
        job
        for job in relevant_jobs
        if job_id(job) not in seen
    ]

    print(f"Found {len(new_jobs)} new internships.")

    for job in new_jobs:
        print(f"NEW: {job['company']} - {job['role']}")

        send_discord(job)
        seen.add(job_id(job))

    # Also remember currently existing jobs even if they don't match
    # future filters.
    save_seen(seen)

    print("Done!")


if __name__ == "__main__":
    main()
