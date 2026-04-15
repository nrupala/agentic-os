"""
GitHub Intelligence Scanner
Scans GitHub for top-starred skills, MD files, and AI agent patterns.
Runs monthly to keep Paradise Stack updated with latest innovations.
"""

import os
import json
import asyncio
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import re

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Paradise-Stack-Intelligence-Scanner"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

SEARCH_QUERIES = [
    "SKILL.md in:path stars:>100",
    "skill in:path stars:>50",
    "claude code skills stars:>100",
    "AI agent prompts stars:>200",
    "CLAUDE.md in:path stars:>50",
    "agent system prompt stars:>100",
    "engineering team agent stars:>50",
    "multi-agent system stars:>100",
    "autonomous AI agent stars:>500",
    "AI coding assistant stars:>1000",
    "software engineering agent stars:>200",
    "DevOps agent stars:>100",
    "marketing automation agent stars:>50",
]

REPOSITORIES = {
    "skill_extraction": "C:\\Users\\HomeUser\\Downloads\\agentic-OS\\intelligence\\skills",
    "agent_prompts": "C:\\Users\\HomeUser\\Downloads\\agentic-OS\\intelligence\\prompts",
    "patterns": "C:\\Users\\HomeUser\\Downloads\\agentic-OS\\intelligence\\patterns",
    "reports": "C:\\Users\\HomeUser\\Downloads\\agentic-OS\\intelligence\\reports",
    "cache": "C:\\Users\\HomeUser\\Downloads\\agentic-OS\\intelligence\\cache",
}

INTELLIGENCE_DIR = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS\\intelligence")

class GitHubIntelligenceScanner:
    def __init__(self):
        self.intelligence_dir = INTELLIGENCE_DIR
        self._ensure_directories()
        
    def _ensure_directories(self):
        for dir_path in REPOSITORIES.values():
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    async def search_github(self, query: str, per_page: int = 30) -> List[Dict]:
        """Search GitHub API for repositories matching query."""
        url = "https://api.github.com/search/repositories"
        params = {"q": query, "per_page": per_page, "sort": "stars", "order": "desc"}
        
        async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("items", [])
            except httpx.HTTPStatusError as e:
                print(f"GitHub API error: {e.response.status_code}")
                return []
            except Exception as e:
                print(f"Search error: {e}")
                return []
    
    async def get_repository_contents(self, owner: str, repo: str, path: str = "") -> List[Dict]:
        """Get repository contents."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching contents: {e}")
                return []
    
    async def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get raw file content from repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and data.get("encoding") == "base64":
                    import base64
                    return base64.b64decode(data["content"]).decode("utf-8")
                return None
            except Exception as e:
                return None
    
    async def find_skill_files(self, owner: str, repo: str) -> List[Dict]:
        """Find SKILL.md and similar skill files in repository."""
        skill_files = []
        
        async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
            try:
                response = await client.get(
                    f"https://api.github.com/search/code",
                    params={"q": f"repo:{owner}/{repo} (SKILL.md OR CLAUDE.md OR skill.md) in:path"}
                )
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("items", [])[:10]:
                        skill_files.append({
                            "name": item["name"],
                            "path": item["path"],
                            "url": item["html_url"],
                            "sha": item["sha"]
                        })
            except Exception:
                pass
        
        return skill_files
    
    async def fetch_and_save_skill(self, repo: Dict, skill_file: Dict) -> Optional[str]:
        """Fetch a skill file and save it locally."""
        owner = repo["full_name"].split("/")[0]
        repo_name = repo["full_name"].split("/")[1]
        
        content = await self.get_file_content(owner, repo_name, skill_file["path"])
        if not content:
            return None
        
        safe_name = re.sub(r'[^\w\-_.]', '_', repo["full_name"])
        safe_path = re.sub(r'[^\w\-_.]', '_', skill_file["path"])
        filename = f"{safe_name}_{safe_path}"
        
        skill_path = Path(REPOSITORIES["skill_extraction"]) / filename
        skill_path.write_text(content, encoding="utf-8")
        
        return str(skill_path)
    
    async def extract_features(self, content: str, repo: Dict) -> Dict:
        """Extract features and patterns from skill/prompt content."""
        features = {
            "source_repo": repo["full_name"],
            "stars": repo.get("stargazers_count", 0),
            "description": repo.get("description", ""),
            "url": repo["html_url"],
            "scanned_at": datetime.now().isoformat(),
            "patterns_found": [],
            "tools_mentioned": [],
            "techniques": [],
            "agent_types": [],
        }
        
        tools_patterns = [
            r"(?:tool|function|plugin|extension|integration):\s*(\w+)",
            r"(?:uses?|using)\s+(\w+(?:\s+\w+)?)",
        ]
        for pattern in tools_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            features["tools_mentioned"].extend(matches[:5])
        
        technique_patterns = [
            r"(?:technique|method|approach|strategy):\s*([^\n]+)",
            r"(?:pattern|pattern):\s*([^\n]+)",
        ]
        for pattern in technique_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            features["techniques"].extend([m.strip() for m in matches[:5]])
        
        agent_patterns = [
            r"(?:agent|persona|role):\s*(\w+)",
            r"(?:engineer|developer|designer|architect|guardian|orchestrator)",
        ]
        for pattern in agent_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            features["agent_types"].extend(matches[:5])
        
        return features
    
    async def scan_all_queries(self) -> List[Dict]:
        """Scan GitHub with all search queries and aggregate results."""
        all_results = []
        seen_repos = set()
        
        for query in SEARCH_QUERIES:
            print(f"Searching: {query}")
            results = await self.search_github(query)
            
            for repo in results:
                if repo["full_name"] not in seen_repos:
                    seen_repos.add(repo["full_name"])
                    all_results.append({
                        "full_name": repo["full_name"],
                        "description": repo.get("description", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "url": repo["html_url"],
                        "language": repo.get("language", ""),
                        "updated": repo.get("updated_at", ""),
                    })
            
            await asyncio.sleep(1)
        
        all_results.sort(key=lambda x: x["stars"], reverse=True)
        return all_results[:50]
    
    async def analyze_repository(self, repo: Dict) -> Dict:
        """Deep analyze a repository for skills and patterns."""
        owner = repo["full_name"].split("/")[0]
        repo_name = repo["full_name"].split("/")[1]
        
        analysis = {
            "repo": repo,
            "skill_files": [],
            "features": [],
            "saved_skills": [],
        }
        
        skill_files = await self.find_skill_files(owner, repo_name)
        analysis["skill_files"] = skill_files
        
        for skill_file in skill_files[:3]:
            path = await self.fetch_and_save_skill(repo, skill_file)
            if path:
                analysis["saved_skills"].append(path)
                
                content = Path(path).read_text(encoding="utf-8")
                features = await self.extract_features(content, repo)
                analysis["features"].append(features)
        
        return analysis
    
    async def run_monthly_scan(self) -> Dict:
        """Run full monthly intelligence scan."""
        print(f"[{datetime.now().isoformat()}] Starting monthly GitHub intelligence scan")
        
        top_repos = await self.scan_all_queries()
        
        report = {
            "scan_date": datetime.now().isoformat(),
            "queries_searched": len(SEARCH_QUERIES),
            "repositories_found": len(top_repos),
            "top_repositories": top_repos[:10],
            "analysis_results": [],
            "total_skills_saved": 0,
        }
        
        for repo in top_repos[:10]:
            print(f"Analyzing: {repo['full_name']} ({repo['stars']} stars)")
            analysis = await self.analyze_repository(repo)
            report["analysis_results"].append(analysis)
            report["total_skills_saved"] += len(analysis["saved_skills"])
            await asyncio.sleep(0.5)
        
        self._save_report(report)
        self._update_cache(report)
        
        print(f"Scan complete. Saved {report['total_skills_saved']} skills")
        return report
    
    def _save_report(self, report: Dict):
        """Save scan report to intelligence/reports."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(REPOSITORIES["reports"]) / f"scan_report_{timestamp}.json"
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        latest_path = Path(REPOSITORIES["reports"]) / "latest.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Report saved: {report_path}")
    
    def _update_cache(self, report: Dict):
        """Update cached intelligence data."""
        cache = {
            "last_scan": report["scan_date"],
            "next_scan_due": (datetime.now() + timedelta(days=30)).isoformat(),
            "top_repos": report["top_repositories"],
            "total_skills": report["total_skills_saved"],
        }
        
        cache_path = Path(REPOSITORIES["cache"]) / "intelligence_cache.json"
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    
    def get_cached_intelligence(self) -> Optional[Dict]:
        """Get cached intelligence data."""
        cache_path = Path(REPOSITORIES["cache"]) / "intelligence_cache.json"
        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    
    def check_scan_needed(self) -> bool:
        """Check if monthly scan is due."""
        cache = self.get_cached_intelligence()
        if not cache:
            return True
        
        last_scan = datetime.fromisoformat(cache["last_scan"])
        days_since = (datetime.now() - last_scan).days
        return days_since >= 30
    
    def generate_skills_index(self) -> str:
        """Generate an index of all saved skills."""
        skills_dir = Path(REPOSITORIES["skill_extraction"])
        index = {
            "generated": datetime.now().isoformat(),
            "skills_count": 0,
            "skills": []
        }
        
        for skill_file in skills_dir.glob("*"):
            if skill_file.is_file():
                skill_entry = {
                    "filename": skill_file.name,
                    "path": str(skill_file),
                    "size": skill_file.stat().st_size,
                    "modified": datetime.fromtimestamp(skill_file.stat().st_mtime).isoformat(),
                }
                index["skills"].append(skill_entry)
                index["skills_count"] += 1
        
        index_path = Path(REPOSITORIES["skill_extraction"]) / "skills_index.json"
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
        
        return str(index_path)


async def main():
    scanner = GitHubIntelligenceScanner()
    
    if scanner.check_scan_needed():
        report = await scanner.run_monthly_scan()
    else:
        cache = scanner.get_cached_intelligence()
        print(f"Using cached data from {cache['last_scan']}")
        print(f"Next scan due: {cache['next_scan_due']}")
        report = cache
    
    index_path = scanner.generate_skills_index()
    print(f"Skills index: {index_path}")
    
    return report


if __name__ == "__main__":
    asyncio.run(main())
