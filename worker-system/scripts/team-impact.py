#!/usr/bin/env python
"""Team-impact metrics — tickets closed per ACTIVE day/week, before vs after the
autonomous-teams cutover, for any Jira project (or all).

"Active" = only days/weeks where >=1 ticket was closed, so the sparse manual era
isn't diluted by zero-days — it compares *intensity on days work happened*, which is
the fair before/after question.

Source: Jira REST (resolutiondate of Done issues). Read-only. Self-contained — no
dependency on any project repo being cloned.

    python scripts/team-impact.py --cutover 2026-06-08 --projects PROJ
    python scripts/team-impact.py --cutover 2026-06-08 --projects PROJ,OPS
    python scripts/team-impact.py --cutover 2026-06-08 --projects PROJ --since 2026-03-01

Env:
    JIRA_BASE_URL              your Jira host, e.g. https://your-org.atlassian.net (required)
    JIRA_EMAIL, JIRA_TOKEN     Jira Basic-auth credentials (required)
"""
from __future__ import annotations

import os
import sys
import json
import base64
import argparse
from datetime import date, datetime, timezone, timedelta
from urllib import request, error

_HOST = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
JIRA_BASE = f"{_HOST}/rest/api/3" if _HOST else None


def _auth() -> str:
    if not JIRA_BASE:
        sys.exit("Set JIRA_BASE_URL in the environment (e.g. https://your-org.atlassian.net).")
    email, token = os.environ.get("JIRA_EMAIL"), os.environ.get("JIRA_TOKEN")
    if not (email and token):
        sys.exit("JIRA_EMAIL and JIRA_TOKEN must be set in the environment.")
    return base64.b64encode(f"{email}:{token}".encode()).decode()


def jira_resolved_dates(project: str, since: str, end: str, auth: str) -> list[date]:
    """Return the resolution dates of every resolved issue in [since, end] for a project."""
    jql = (f'project = {project} AND resolutiondate >= "{since}" '
           f'AND resolutiondate <= "{end} 23:59" ORDER BY resolutiondate ASC')
    out: list[date] = []
    next_token = None
    while True:
        payload = {"jql": jql, "fields": ["resolutiondate"], "maxResults": 100}
        if next_token:
            payload["nextPageToken"] = next_token
        req = request.Request(
            f"{JIRA_BASE}/search/jql", data=json.dumps(payload).encode(),
            headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json",
                     "Accept": "application/json"}, method="POST")
        try:
            with request.urlopen(req) as r:
                data = json.load(r)
        except error.HTTPError as e:
            sys.exit(f"Jira API error ({e.code}) for {project}: {e.read().decode()[:200]}")
        for issue in data.get("issues", []):
            rd = (issue.get("fields") or {}).get("resolutiondate")
            if rd:
                out.append(date.fromisoformat(rd[:10]))
        next_token = data.get("nextPageToken")
        if not next_token:
            break
    return out


def stats(dates: list[date]) -> dict:
    n = len(dates)
    active_days = len(set(dates))
    active_weeks = len({(d.isocalendar()[0], d.isocalendar()[1]) for d in dates})
    return {
        "tickets": n,
        "active_days": active_days,
        "active_weeks": active_weeks,
        "per_active_day": round(n / active_days, 2) if active_days else 0.0,
        "per_active_week": round(n / active_weeks, 2) if active_weeks else 0.0,
    }


def fmt_ratio(after: float, before: float) -> str:
    if not before:
        return "n/a (no before-data)"
    return f"{after / before:.1f}x"


def report(label: str, before: list[date], after: list[date]) -> None:
    b, a = stats(before), stats(after)
    print(f"\n=== {label} ===")
    print(f"  {'period':6s} {'tickets':>7s} {'act.days':>8s} {'/day':>6s} {'act.wks':>7s} {'/week':>7s}")
    print(f"  {'before':6s} {b['tickets']:7d} {b['active_days']:8d} {b['per_active_day']:6.2f} "
          f"{b['active_weeks']:7d} {b['per_active_week']:7.2f}")
    print(f"  {'after':6s} {a['tickets']:7d} {a['active_days']:8d} {a['per_active_day']:6.2f} "
          f"{a['active_weeks']:7d} {a['per_active_week']:7.2f}")
    print(f"  impact: {fmt_ratio(a['per_active_day'], b['per_active_day'])}/active-day, "
          f"{fmt_ratio(a['per_active_week'], b['per_active_week'])}/active-week")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Before/after team-impact (tickets per active day/week)")
    p.add_argument("--cutover", required=True, help="autonomous-teams start date, YYYY-MM-DD")
    p.add_argument("--projects", required=True,
                   help="comma-separated Jira project keys, e.g. PROJ,OPS")
    p.add_argument("--since", help="analysis start date (default: cutover - 120d)")
    p.add_argument("--end", help="analysis end date (default: today)")
    args = p.parse_args(argv)

    cutover = date.fromisoformat(args.cutover)
    since = args.since or (cutover - timedelta(days=120)).isoformat()
    end = args.end or datetime.now(timezone.utc).date().isoformat()
    projects = [x.strip().upper() for x in args.projects.split(",") if x.strip()]
    auth = _auth()

    print(f"Team-impact (before/after) - cutover {cutover}, window {since} to {end}; active days/weeks only")
    pooled_before: list[date] = []
    pooled_after: list[date] = []
    for proj in projects:
        dates = jira_resolved_dates(proj, since, end, auth)
        before = [d for d in dates if d < cutover]
        after = [d for d in dates if d >= cutover]
        if not dates:
            print(f"\n=== {proj} ===  (no resolved issues in window)")
            continue
        report(proj, before, after)
        pooled_before += before
        pooled_after += after

    if len(projects) > 1:
        report("ALL (fleet pooled)", pooled_before, pooled_after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
