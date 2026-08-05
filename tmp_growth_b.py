import datetime
import json
import os

import requests

handle = os.environ["BLUESKY_HANDLE"]
password = os.environ["BLUESKY_PASSWORD"]

sess = requests.post(
    "https://bsky.social/xrpc/com.atproto.server.createSession",
    json={"identifier": handle, "password": password},
    timeout=30,
)
sess.raise_for_status()
token = sess.json()["accessJwt"]
headers = {"Authorization": f"Bearer {token}"}

since = (
    datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=48)
).strftime("%Y-%m-%dT%H:%M:%SZ")

queries = [
    "stumped on a gift",
    "terrible at gifts",
    "last minute birthday gift",
    "present for my partner",
    "wedding gift ideas",
    "gift for grandpa",
]

for q in queries:
    r = requests.get(
        "https://bsky.social/xrpc/app.bsky.feed.searchPosts",
        params={"q": q, "sort": "latest", "since": since, "limit": 10},
        headers=headers,
        timeout=30,
    )
    if r.status_code != 200:
        print(f"[{q}] HTTP {r.status_code}: {r.text[:200]}")
        continue
    posts = r.json().get("posts", [])
    print(f"[{q}] {len(posts)} posts")
    for p in posts:
        author = p["author"]["handle"]
        text = p["record"].get("text", "").replace("\n", " ")
        created = p["record"].get("createdAt", "")
        uri = p["uri"]
        print(f"  - @{author} {created}\n    {text[:300]}\n    {uri}")
