"""
Paradise Stack Web Dashboard - Full Featured
Interactive web interface with workflow management, task console, and GitHub integration.
"""

from flask import Flask, render_template, jsonify, request
import os
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS")
INTELLIGENCE_DIR = PROJECT_ROOT / "intelligence"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

sys.path.insert(0, str(PROJECT_ROOT))

def safe_divide(numerator, denominator, default=0):
    """Safe division with divide-by-zero protection."""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default

def get_system_state():
    """Get current Paradise Stack state with error handling."""
    state = {
        "evolution_level": 1,
        "skills_integrated": 0,
        "patterns_mastered": 0,
        "knowledge_age_days": 0,
        "top_patterns": [],
        "intelligence_ready": False,
        "total_workflows": 0,
        "active_workflows": 0,
        "total_deliverables": 0,
    }
    
    try:
        from cognition.continuous_intelligence import initialize_evolution
        engine = initialize_evolution()
        if engine:
            evo_state = engine.get_evolved_state()
            state.update({
                "evolution_level": safe_divide(evo_state.get("evolution_level", 1), 1, 1),
                "skills_integrated": evo_state.get("skills_integrated", 0),
                "patterns_mastered": evo_state.get("patterns_mastered", 0),
                "knowledge_age_days": evo_state.get("knowledge_age_days", 0),
                "top_patterns": evo_state.get("top_patterns", [])[:5],
                "intelligence_ready": True,
            })
    except Exception as e:
        state["error"] = str(e)
    
    try:
        outputs = list(OUTPUT_DIR.glob("wf_*"))
        state["total_workflows"] = len(outputs)
        
        workflows = []
        for out in outputs:
            manifest = out / "manifest.json"
            if manifest.exists():
                try:
                    with open(manifest, 'r') as f:
                        workflows.append(json.load(f))
                except:
                    pass
        
        state["active_workflows"] = sum(1 for w in workflows if w.get("status") == "completed")
        
        deliverables = []
        for wf in workflows:
            for d in wf.get("deliverables", []):
                if d:
                    deliverables.append(d)
        state["total_deliverables"] = len(deliverables)
    except Exception as e:
        state["workflows_error"] = str(e)
    
    cache_file = INTELLIGENCE_DIR / "cache" / "intelligence_cache.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                state["last_scan"] = cache.get("last_scan", "Never")
                state["next_scan"] = cache.get("next_scan_due", "Not scheduled")
                state["repositories_found"] = safe_divide(len(cache.get("top_repos", [])), 1, 0)
        except Exception as e:
            state["cache_error"] = str(e)
    else:
        state["last_scan"] = "Never"
        state["next_scan"] = "Not scheduled"
        state["repositories_found"] = 0
    
    return state


def get_workflows():
    """Get all workflows with error handling."""
    workflows = []
    try:
        outputs = list(OUTPUT_DIR.glob("wf_*"))
        for out in sorted(outputs, key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
            manifest = out / "manifest.json"
            if manifest.exists():
                try:
                    with open(manifest, 'r') as f:
                        wf = json.load(f)
                        wf["output_dir"] = str(out)
                        workflows.append(wf)
                except Exception:
                    pass
    except Exception:
        pass
    return workflows


def get_deliverables():
    """Get all deliverables with error handling."""
    deliverables = []
    try:
        workflows = get_workflows()
        for wf in workflows:
            for d in wf.get("deliverables", []):
                if d and isinstance(d, dict):
                    d["workflow_id"] = wf.get("workflow_id", "unknown")
                    d["task"] = wf.get("task", "Unknown task")
                    deliverables.append(d)
    except Exception:
        pass
    return deliverables


@app.route('/')
def index():
    """Main dashboard page."""
    state = get_system_state()
    skills = get_skills_index()
    repos = get_repositories()
    workflows = get_workflows()[:10]
    deliverables = get_deliverables()[:10]
    
    return render_template(
        'dashboard.html',
        state=state,
        skills=skills,
        repos=repos,
        workflows=workflows,
        deliverables=deliverables,
        datetime=datetime,
        len=len,
        str=str,
    )


def get_skills_index():
    """Get skills index with error handling."""
    index_file = INTELLIGENCE_DIR / "skills" / "skills_index.json"
    if index_file.exists():
        try:
            with open(index_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {"skills_count": 0, "skills": []}
    return {"skills_count": 0, "skills": []}


def get_repositories():
    """Get top repositories with error handling."""
    cache_file = INTELLIGENCE_DIR / "cache" / "intelligence_cache.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                repos = cache.get("top_repos", [])
                return sorted(repos, key=lambda x: safe_divide(x.get("stars", 0), 1, 0), reverse=True)[:10]
        except Exception:
            return []
    return []


@app.route('/api/state')
def api_state():
    """API endpoint for system state."""
    return jsonify(get_system_state())


@app.route('/api/workflows')
def api_workflows():
    """API endpoint for workflows."""
    return jsonify(get_workflows())


@app.route('/api/deliverables')
def api_deliverables():
    """API endpoint for deliverables."""
    return jsonify(get_deliverables())


@app.route('/api/skills')
def api_skills():
    """API endpoint for skills."""
    return jsonify(get_skills_index())


@app.route('/api/repos')
def api_repos():
    """API endpoint for repositories."""
    return jsonify(get_repositories())


@app.route('/api/workflow/create', methods=['POST'])
def api_workflow_create():
    """Create and run a new workflow."""
    try:
        from paradise_unified import ParadiseUnifiedInterface
        
        data = request.json or {}
        task = data.get("task", "Untitled task")
        
        interface = ParadiseUnifiedInterface()
        workflow = interface.run(task)
        
        return jsonify({
            "success": True,
            "workflow_id": workflow.id,
            "task": workflow.task,
            "status": workflow.status,
            "deliverables_count": len(workflow.deliverables),
            "output_dir": workflow.output_dir,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/deliverable/<deliverable_id>')
def api_deliverable(deliverable_id):
    """Get deliverable details."""
    deliverables = get_deliverables()
    for d in deliverables:
        if d.get("id") == deliverable_id:
            return jsonify({"success": True, "deliverable": d})
    return jsonify({"success": False, "error": "Not found"}), 404


@app.route('/api/deliverable/<deliverable_id>/content')
def api_deliverable_content(deliverable_id):
    """Get deliverable content."""
    deliverables = get_deliverables()
    for d in deliverables:
        if d.get("id") == deliverable_id:
            path = Path(d.get("path", ""))
            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8")
                    return jsonify({
                        "success": True,
                        "content": content,
                        "size": len(content),
                        "lines": content.count('\n') + 1,
                    })
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
            return jsonify({"success": False, "error": "File not found"}), 404
    return jsonify({"success": False, "error": "Not found"}), 404


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Prepare GitHub upload."""
    github_token = os.environ.get("GITHUB_TOKEN")
    
    if not github_token:
        return jsonify({
            "success": False,
            "error": "GITHUB_TOKEN not set. Set with: $env:GITHUB_TOKEN = 'your_token'"
        }), 400
    
    data = request.json or {}
    deliverable_id = data.get("deliverable_id")
    repo = data.get("repo", "user/paradise-output")
    
    if not deliverable_id:
        return jsonify({"success": False, "error": "deliverable_id required"}), 400
    
    deliverables = get_deliverables()
    for d in deliverables:
        if d.get("id") == deliverable_id:
            return jsonify({
                "success": True,
                "message": "GitHub integration ready",
                "file": d.get("name"),
                "path": d.get("path"),
                "repo": repo,
                "note": "Configure GitHub credentials to enable upload"
            })
    
    return jsonify({"success": False, "error": "Deliverable not found"}), 404


@app.route('/api/evolve', methods=['POST'])
def api_evolve():
    """Record evolution."""
    try:
        from cognition.continuous_intelligence import initialize_evolution
        
        engine = initialize_evolution()
        data = request.json or {}
        
        interaction = {
            "type": data.get("type", "user_interaction"),
            "content": data.get("content", ""),
            "outcome": data.get("outcome", "processed"),
            "timestamp": datetime.now().isoformat(),
        }
        
        engine.evolve_from_interaction(interaction)
        state = engine.get_evolved_state()
        
        return jsonify({
            "success": True,
            "evolution_level": state.get("evolution_level", 1),
            "patterns_mastered": state.get("patterns_mastered", 0),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def create_dashboard():
    """Create the dashboard HTML template."""
    templates_dir = PROJECT_ROOT / "dashboard" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paradise Stack v2.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #0f0f14; --card: #1a1a24; --border: #2a2a3a;
            --accent: #6366f1; --success: #22c55e; --warning: #eab308; --error: #ef4444;
            --text: #e2e8f0; --dim: #64748b;
        }
        body { font-family: system-ui; background: var(--bg); color: var(--text); min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; padding: 1.5rem; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }
        h1 { font-size: 1.5rem; background: linear-gradient(135deg, var(--accent), #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; }
        .stat { font-size: 2rem; font-weight: 700; }
        .label { color: var(--dim); font-size: 0.875rem; margin-top: 0.25rem; }
        .section { margin-bottom: 2rem; }
        .section-title { font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; }
        .btn { background: var(--accent); color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 500; }
        .btn:hover { opacity: 0.9; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-secondary { background: var(--card); border: 1px solid var(--border); color: var(--text); }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 0.75rem; border-bottom: 1px solid var(--border); }
        th { color: var(--dim); font-weight: 500; font-size: 0.75rem; text-transform: uppercase; }
        .status { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 500; }
        .status-completed { background: rgba(34,197,94,0.2); color: var(--success); }
        .status-pending { background: rgba(234,179,8,0.2); color: var(--warning); }
        .status-failed { background: rgba(239,68,68,0.2); color: var(--error); }
        .badge { background: var(--accent); color: white; padding: 0.125rem 0.5rem; border-radius: 4px; font-size: 0.75rem; }
        .progress { height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; margin-top: 0.5rem; }
        .progress-bar { height: 100%; background: linear-gradient(90deg, var(--accent), #a855f7); transition: width 0.3s; }
        .tab-container { margin-bottom: 1rem; }
        .tab { display: inline-block; padding: 0.5rem 1rem; cursor: pointer; border-bottom: 2px solid transparent; color: var(--dim); }
        .tab.active { color: var(--accent); border-color: var(--accent); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 100; align-items: center; justify-content: center; }
        .modal.active { display: flex; }
        .modal-content { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 2rem; max-width: 500px; width: 90%; }
        .modal-title { font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; }
        input, textarea { width: 100%; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem; color: var(--text); margin-bottom: 1rem; }
        textarea { min-height: 100px; resize: vertical; }
        .modal-actions { display: flex; gap: 1rem; justify-content: flex-end; }
        .code-block { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 1rem; font-family: monospace; font-size: 0.875rem; max-height: 300px; overflow: auto; white-space: pre-wrap; }
        .empty { text-align: center; padding: 2rem; color: var(--dim); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Paradise Stack v2.0</h1>
            <button class="btn" onclick="openCreateModal()">+ New Workflow</button>
        </header>
        
        <div class="grid">
            <div class="card">
                <div class="stat" id="stat-level">{{ state.evolution_level }}</div>
                <div class="label">Evolution Level</div>
                <div class="progress"><div class="progress-bar" style="width: {{ state.evolution_level * 10 }}%"></div></div>
            </div>
            <div class="card">
                <div class="stat" id="stat-workflows">{{ state.total_workflows }}</div>
                <div class="label">Total Workflows</div>
            </div>
            <div class="card">
                <div class="stat" id="stat-deliverables">{{ state.total_deliverables }}</div>
                <div class="label">Deliverables</div>
            </div>
            <div class="card">
                <div class="stat" id="stat-repos">{{ state.repositories_found }}</div>
                <div class="label">Repositories</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">
                Workflows
                <button class="btn btn-secondary" onclick="refreshData()">Refresh</button>
            </div>
            <div class="card">
                <table id="workflows-table">
                    <thead>
                        <tr>
                            <th>Task</th>
                            <th>Status</th>
                            <th>Steps</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if workflows %}
                        {% for wf in workflows %}
                        <tr>
                            <td>{{ wf.task[:50] }}{% if wf.task|length > 50 %}...{% endif %}</td>
                            <td><span class="status status-{{ wf.status }}">{{ wf.status }}</span></td>
                            <td>{{ wf.steps|length if wf.steps else 0 }}</td>
                            <td>{{ wf.created_at[:10] if wf.created_at else 'N/A' }}</td>
                            <td>
                                <button class="btn btn-secondary" onclick="viewWorkflow(\'{{ wf.workflow_id }}\')">View</button>
                                <button class="btn btn-secondary" onclick="testDeliverables(\'{{ wf.workflow_id }}\')">Test</button>
                            </td>
                        </tr>
                        {% endfor %}
                        {% else %}
                        <tr><td colspan="5" class="empty">No workflows yet. Create one to get started.</td></tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Deliverables</div>
            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Size</th>
                            <th>Workflow</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if deliverables %}
                        {% for d in deliverables %}
                        <tr>
                            <td>{{ d.name }}</td>
                            <td><span class="badge">{{ d.type }}</span></td>
                            <td>{{ "%.1f"|format(d.size / 1024) if d.size else 0 }} KB</td>
                            <td>{{ d.task[:30] }}...</td>
                            <td>
                                <button class="btn btn-secondary" onclick="viewContent(\'{{ d.id }}\')">View</button>
                                <button class="btn btn-secondary" onclick="uploadFile(\'{{ d.id }}\')">Upload</button>
                            </td>
                        </tr>
                        {% endfor %}
                        {% else %}
                        <tr><td colspan="5" class="empty">No deliverables yet.</td></tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Top Repositories</div>
            <div class="card">
                <table>
                    <thead>
                        <tr><th>Repository</th><th>Description</th><th>Stars</th></tr>
                    </thead>
                    <tbody>
                        {% for repo in repos %}
                        <tr>
                            <td>{{ repo.full_name }}</td>
                            <td>{{ repo.description[:60] if repo.description else '' }}...</td>
                            <td><span class="badge">{{ "{:,}".format(repo.stars) }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="modal" id="create-modal">
        <div class="modal-content">
            <div class="modal-title">Create Workflow</div>
            <input type="text" id="task-input" placeholder="What would you like me to build?">
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="closeModal(\'create-modal\')">Cancel</button>
                <button class="btn" onclick="createWorkflow()" id="create-btn">Create</button>
            </div>
        </div>
    </div>
    
    <div class="modal" id="content-modal">
        <div class="modal-content">
            <div class="modal-title">File Content</div>
            <div class="code-block" id="content-view">Loading...</div>
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="closeModal(\'content-modal\')">Close</button>
            </div>
        </div>
    </div>

    <script>
        function openCreateModal() {
            document.getElementById(\'create-modal\').classList.add(\'active\');
            document.getElementById(\'task-input\').focus();
        }
        
        function closeModal(id) {
            document.getElementById(id).classList.remove(\'active\');
        }
        
        async function createWorkflow() {
            const task = document.getElementById(\'task-input\').value.trim();
            if (!task) return alert(\'Please enter a task\');
            
            const btn = document.getElementById(\'create-btn\');
            btn.disabled = true;
            btn.textContent = \'Creating...\';
            
            try {
                const res = await fetch(\'/api/workflow/create\', {
                    method: \'POST\',
                    headers: {\'Content-Type\': \'application/json\'},
                    body: JSON.stringify({task})
                });
                const data = await res.json();
                if (data.success) {
                    alert(\'Workflow created: \' + data.workflow_id);
                    location.reload();
                } else {
                    alert(\'Error: \' + data.error);
                }
            } catch (e) {
                alert(\'Error: \' + e);
            }
            
            btn.disabled = false;
            btn.textContent = \'Create\';
        }
        
        async function viewContent(id) {
            try {
                const res = await fetch(\'/api/deliverable/\' + id + \'/content\');
                const data = await res.json();
                if (data.success) {
                    document.getElementById(\'content-view\').textContent = data.content;
                    document.getElementById(\'content-modal\').classList.add(\'active\');
                } else {
                    alert(\'Error: \' + data.error);
                }
            } catch (e) {
                alert(\'Error: \' + e);
            }
        }
        
        async function uploadFile(id) {
            const repo = prompt(\'GitHub repo (e.g., user/repo):\', \'user/paradise-output\');
            if (!repo) return;
            
            try {
                const res = await fetch(\'/api/upload\', {
                    method: \'POST\',
                    headers: {\'Content-Type\': \'application/json\'},
                    body: JSON.stringify({deliverable_id: id, repo})
                });
                const data = await res.json();
                if (data.success) {
                    alert(\'Upload prepared: \' + data.message + \'\\nFile: \' + data.file);
                } else {
                    alert(\'Error: \' + data.error);
                }
            } catch (e) {
                alert(\'Error: \' + e);
            }
        }
        
        async function refreshData() {
            location.reload();
        }
        
        async function viewWorkflow(id) {
            alert(\'View workflow: \' + id);
        }
        
        async function testDeliverables(id) {
            alert(\'Test deliverables for: \' + id);
        }
        
        document.addEventListener(\'keydown\', (e) => {
            if (e.key === \'Escape\') {
                document.querySelectorAll(\'.modal\').forEach(m => m.classList.remove(\'active\'));
            }
        });
    </script>
</body>
</html>'''
    
    with open(templates_dir / 'dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Dashboard template created at: {templates_dir / 'dashboard.html'}")


if __name__ == '__main__':
    create_dashboard()
    app.run(debug=True, host='0.0.0.0', port=5000)
