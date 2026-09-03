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

# Roles for now are SWE and Data Science related. This can be expanded later

ROLE_CATEGORIES = {
    "Software Engineering": [
        "software engineer",
        "software engineering",
        "software developer",
        "swe intern",
        "full stack",
        "fullstack",
        "backend",
        "back end",
        "frontend",
        "front end",
        "web developer",
        "mobile engineer",
        "ios engineer",
        "android engineer",
    ],

    "AI / Machine Learning": [
        "machine learning",
        "ml engineer",
        "artificial intelligence",
        "ai engineer",
        "computer vision",
        "deep learning",
        "nlp",
        "natural language processing",
    ],

    "Data": [
        "data engineer",
        "data scientist",
        "data science",
        "analytics engineer",
        "data platform",
    ],

    "Cloud / Infrastructure": [
        "cloud engineer",
        "platform engineer",
        "devops",
        "site reliability",
        "sre",
        "infrastructure engineer",
        "infrastructure software",
    ],

    "Cybersecurity": [
        "security engineer",
        "cybersecurity",
        "cyber security",
        "application security",
        "information security",
        "security analyst",
        "product security",
    ],

    "Systems / Firmware": [
        "firmware engineer",
        "firmware",
        "embedded software",
        "embedded systems",
        "systems software",
        "system software",
        "kernel",
        "operating systems",
    ],
}

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

    soup = BeautifulSoup(readme, "html.parser")

    for row in soup.find_all("tr"):
        columns = row.find_all("td")

        # Expected:
        # Company | Role | Location | Application | Age
        if len(columns) < 4:
            continue

        company = columns[0].get_text(" ", strip=True)
        role = columns[1].get_text(" ", strip=True)
        location = columns[2].get_text(", ", strip=True)

        # Simplify sometimes uses ↳ for another position
        # at the same company.
        if company == "↳":
            company = "Same company as above"

        application_links = columns[3].find_all("a", href=True)

        if not application_links:
            continue

        # First link is normally the direct employer application.
        link = application_links[0]["href"]

        jobs.append({
            "company": company,
            "role": role,
            "location": location,
            "link": link,
            "source": "Simplify",
        })

    return jobs


def get_category(job):
    role = job["role"].lower()

    for category, keywords in ROLE_CATEGORIES.items():
        if any(keyword in role for keyword in keywords):
            return category

    return None


def is_relevant(job):
    return get_category(job) is not None


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
    category = get_category(job) or "Other"
    if not WEBHOOK_URL:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not set.")

    payload = {
        "embeds": [
            {
                "title": "Alert: New Summer 2027 Internship",
                "description": f"{category}\n\n**{job['role']}**",
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

#test
def send_test_notification():
    test_job = {
        "company": "Test Company",
        "role": "Software Engineer Intern",
        "location": "New York, NY",
        "link": "https://github.com/SimplifyJobs/Summer2027-Internships",
    }

    print("Sending test internship notification...")
    send_discord(test_job)
    print("Test notification sent!")


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
        if not relevant_jobs:
            print("ERROR: No jobs were parsed.")
            print("Refusing to initialize an empty database.")
            return

        seen = {job_id(job) for job in relevant_jobs}

        save_seen(seen)

        print("Initial job database created.")
        print(f"Saved {len(seen)} existing internships.")
        print("No Discord notifications sent.")
        return

    new_jobs = [
        job
        for job in relevant_jobs
        if job_id(job) not in seen
    ]

    print(f"Found {len(new_jobs)} new internships.")

    for job in new_jobs:
        print(f"NEW: [{get_category(job)}] {job['company']} - {job['role']}")

        send_discord(job)
        seen.add(job_id(job))

    # Also remember currently existing jobs even if they don't match
    # future filters.
    save_seen(seen)

    print("Done!")


if __name__ == "__main__":
    if os.getenv("TEST_MODE") == "true":
        send_test_notification()
    else:
        main()
