"""
Quick Manual Skill Integrator
Fetches skills directly from top discovered repositories.
"""

import os
import json
import httpx
from pathlib import Path
from datetime import datetime

INTELLIGENCE_DIR = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS\\intelligence")
SKILLS_DIR = INTELLIGENCE_DIR / "skills"
REPOS = [
    {"name": "everything-claude-code", "stars": 155998, "owner": "affaan-m"},
    {"name": "superpowers", "stars": 152157, "owner": "obra"},
    {"name": "system-prompts-and-models-of-ai-tools", "stars": 135173, "owner": "x1xhlol"},
    {"name": "30-seconds-of-code", "stars": 127461, "owner": "Chalarangelo"},
    {"name": "skills", "stars": 117337, "owner": "anthropics"},
    {"name": "Prompt-Engineering-Guide", "stars": 73308, "owner": "dair-ai"},
    {"name": "deer-flow", "stars": 61495, "owner": "bytedance"},
    {"name": "awesome-claude-skills", "stars": 53802, "owner": "ComposioHQ"},
]

async def fetch_readme(owner, repo):
    """Fetch README from a repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    headers = {"Accept": "application/vnd.github.raw+json"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.text
        except:
            pass
    return None

async def main():
    print("Fetching skills from top repositories...")
    skills_found = 0
    
    for repo in REPOS:
        print(f"  {repo['name']} ({repo['stars']:,} stars)...")
        
        content = await fetch_readme(repo["owner"], repo["name"])
        if content:
            # Save the README as a skill source
            skill_file = SKILLS_DIR / f"{repo['owner']}_{repo['name']}.md"
            skill_file.write_text(content[:50000], encoding="utf-8")  # Limit size
            skills_found += 1
            print(f"    + Saved: {skill_file.name}")
        else:
            print(f"    - Rate limited or unavailable")
    
    # Update intelligence cache
    cache = {
        "last_scan": datetime.now().isoformat(),
        "next_scan_due": (datetime.now() + __import__('datetime').timedelta(days=30)).isoformat(),
        "repositories_found": len(REPOS),
        "skills_sourced": skills_found,
        "top_repos": REPOS,
    }
    
    cache_file = INTELLIGENCE_DIR / "cache" / "intelligence_cache.json"
    cache_file.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    
    # Generate index
    index = {"generated": datetime.now().isoformat(), "skills": []}
    for f in SKILLS_DIR.glob("*.md"):
        index["skills"].append({"file": f.name, "size": f.stat().st_size})
    index["skills_count"] = len(index["skills"])
    
    index_file = SKILLS_DIR / "skills_index.json"
    index_file.write_text(json.dumps(index, indent=2), encoding="utf-8")
    
    print(f"\nDone! Saved {skills_found} skill sources.")
    print(f"Total skills indexed: {index['skills_count']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
