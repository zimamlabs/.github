#!/usr/bin/env python3
"""Rewrite the auto sections of profile/README.md from the org's real releases and merged pull requests."""
import json, re, subprocess, sys
ORG = "zimamlabs"
APPS = ["rukn", "dawem", "falah", "zimma", "himma", "rakeb", "rahhala"]

def gh(path):
    out = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    return json.loads(out.stdout) if out.returncode == 0 and out.stdout.strip() else None

def day(iso): return iso[:10]

def nice(title):
    # Pull request titles are branch names such as feat/home-folder-tour.
    kind, _, rest = title.partition("/")
    return f"{kind}: {rest.replace('-', ' ')}" if rest else title

releases, merged = [], []
for app in APPS:
    r = gh(f"repos/{ORG}/{app}/releases/latest")
    if r: releases.append((r["published_at"], app, r["tag_name"], r["html_url"], sum(a["download_count"] for a in r["assets"] if a["name"].endswith(".apk"))))
    prs = gh(f"repos/{ORG}/{app}/pulls?state=closed&per_page=8&sort=updated&direction=desc") or []
    for p in prs:
        if p.get("merged_at"): merged.append((p["merged_at"], app, p["number"], p["title"], p["html_url"]))
releases.sort(reverse=True); merged.sort(reverse=True)

rel = ["| App | Latest | Released |", "|---|---|---|"]
for when, app, tag, url, _ in releases:
    rel.append(f"| **{app.capitalize()}** | [{tag}]({url}) | {day(when)} |")
act = [f"- `{day(when)}` **{app.capitalize()}**: [{nice(title)}]({url})" for when, app, num, title, url in merged[:12]]

p = "profile/README.md"; s = open(p).read()
def put(name, body):
    global s
    s = re.sub(rf"(<!-- {name}:START -->).*?(<!-- {name}:END -->)", lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", s, flags=re.S)
put("RELEASES", "\n".join(rel)); put("ACTIVITY", "\n".join(act))
open(p, "w").write(s)
print(len(releases), "releases,", len(merged), "merged pull requests")
