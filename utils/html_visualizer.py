#!/usr/bin/env python3
"""
HTML Visualizer v3.0 — Clean & Professional

Better color system:
- Warmer grays (not cold slate)
- GitHub-inspired colors
- Better contrast
- Subtle accents (not neon)
- More white space
- Cleaner, more professional

Only shows what matters:
1. Project overview
2. Dependency graph
3. File list
4. Execution order
"""

import json
import os
from datetime import datetime
from typing import Dict, Any


class HTMLVisualizer:
    """Generates clean, professional HTML report."""

    def __init__(self, project_data: Dict[str, Any]):
        self.data = project_data
        self.project_name = project_data.get("project_name", "Project")

    def generate(self, output_path: str) -> str:
        """Generate HTML report."""
        print(f"  🎨 Generating HTML report...")

        graph_data = self._prepare_graph_data()
        html = self._build_html(graph_data)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        file_size = os.path.getsize(output_path) / 1024
        print(f"  ✅ HTML saved: {output_path} ({file_size:.0f} KB)")
        return output_path

    def _prepare_graph_data(self) -> Dict:
        """Prepare graph data."""
        files = self.data.get("files", {})
        dep_graph = self.data.get("dependency_graph", {})

        # Build nodes
        nodes = []
        for rel_path, analysis in files.items():
            nodes.append({
                "id": rel_path,
                "label": os.path.basename(rel_path),
                "lines": analysis.get("line_count", 0),
                "functions": len(analysis.get("functions", [])),
                "classes": len(analysis.get("classes", [])),
            })

        # Build edges
        edges = []
        for source, deps in dep_graph.items():
            for target in deps:
                edges.append({
                    "source": source,
                    "target": target,
                })

        return {"nodes": nodes, "edges": edges}

    def _build_html(self, graph_data) -> str:
        """Build HTML with better color system."""
        files = self.data.get("files", {})
        exec_order = self.data.get("execution_order", [])
        entry_points = self.data.get("entry_points", [])
        requirements = self.data.get("requirements", [])

        total_lines = sum(f.get("line_count", 0) for f in files.values())
        total_functions = sum(len(f.get("functions", [])) for f in files.values())
        total_classes = sum(len(f.get("classes", [])) for f in files.values())

        # Build file list
        file_rows = []
        for rel_path in exec_order:
            analysis = files.get(rel_path, {})
            is_entry = rel_path in entry_points
            entry_badge = '<span class="badge badge-blue">Entry Point</span>' if is_entry else ''
            
            file_rows.append(f"""
                <tr>
                    <td class="file-name">{rel_path} {entry_badge}</td>
                    <td>{analysis.get('line_count', 0)}</td>
                    <td>{len(analysis.get('functions', []))}</td>
                    <td>{len(analysis.get('classes', []))}</td>
                </tr>""")
        file_table_html = "\n".join(file_rows)

        # Build execution order
        exec_items = ""
        for i, f in enumerate(exec_order, 1):
            is_entry = "🎯" if f in entry_points else ""
            exec_items += f'<div class="exec-item"><span class="exec-num">{i}</span><span class="exec-file">{f}</span> {is_entry}</div>'

        # Build requirements list
        req_list = ""
        if requirements:
            req_list = "<ul class='req-list'>"
            for req in requirements[:20]:
                req_list += f"<li>{req}</li>"
            if len(requirements) > 20:
                req_list += f"<li class='more'>... and {len(requirements) - 20} more</li>"
            req_list += "</ul>"
        else:
            req_list = "<p class='no-req'>No external dependencies detected</p>"

        graph_json = json.dumps(graph_data)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self.project_name} — Project Report</title>

<!-- D3.js for graph -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<!-- Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
/* ═══════════════════════════════════════════════════════════
   Better Color System — Warmer, More Professional
   ═══════════════════════════════════════════════════════════ */

:root {{
    /* Warmer grays (not cold slate) */
    --bg-primary: #1a1a1a;
    --bg-secondary: #242424;
    --bg-card: #2a2a2a;
    --bg-hover: #333333;
    
    /* Better text contrast */
    --text-primary: #f5f5f5;
    --text-secondary: #b0b0b0;
    --text-muted: #808080;
    
    /* Subtle borders */
    --border: #3a3a3a;
    --border-light: #444444;
    
    /* GitHub-inspired accents (not neon) */
    --accent-blue: #58a6ff;
    --accent-green: #3fb950;
    --accent-yellow: #d29922;
    --accent-red: #f85149;
    --accent-purple: #bc8cff;
    
    /* Subtle glows */
    --glow-blue: 0 0 12px rgba(88, 166, 255, 0.15);
    --glow-green: 0 0 12px rgba(63, 185, 80, 0.15);
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
}}

/* Typography */
h1 {{
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}}

h2 {{
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

h3 {{
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
}}

/* Header */
.header {{
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    padding: 2rem 0;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}}

.header-content {{
    text-align: center;
}}

.header h1 {{
    color: var(--accent-blue);
}}

.header .subtitle {{
    color: var(--text-secondary);
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
}}

.header .generated {{
    color: var(--text-muted);
    font-size: 0.9rem;
}}

/* Stats Grid */
.stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}}

.stat-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.2s;
}}

.stat-card:hover {{
    border-color: var(--border-light);
    background: var(--bg-hover);
}}

.stat-value {{
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-blue);
    margin-bottom: 0.25rem;
}}

.stat-label {{
    font-size: 0.85rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Sections */
.section {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 2rem;
    margin-bottom: 2rem;
}}

/* Tables */
.table-wrapper {{
    overflow-x: auto;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
}}

thead {{
    background: var(--bg-secondary);
    border-bottom: 2px solid var(--border);
}}

th {{
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
}}

td {{
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
    color: var(--text-primary);
}}

tr:hover td {{
    background: var(--bg-hover);
}}

.file-name {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    color: var(--accent-blue);
}}

/* Badges */
.badge {{
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 0.5rem;
}}

.badge-blue {{
    background: rgba(88, 166, 255, 0.15);
    color: var(--accent-blue);
}}

.badge-green {{
    background: rgba(63, 185, 80, 0.15);
    color: var(--accent-green);
}}

.badge-yellow {{
    background: rgba(210, 153, 34, 0.15);
    color: var(--accent-yellow);
}}

.badge-red {{
    background: rgba(248, 81, 73, 0.15);
    color: var(--accent-red);
}}

/* Execution Order */
.exec-list {{
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}}

.exec-item {{
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    transition: all 0.2s;
}}

.exec-item:hover {{
    border-color: var(--border-light);
    background: var(--bg-hover);
}}

.exec-num {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--accent-blue);
    color: white;
    font-size: 0.85rem;
    font-weight: 700;
    flex-shrink: 0;
}}

.exec-file {{
    flex: 1;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    color: var(--accent-blue);
}}

/* Graph Container */
.graph-container {{
    position: relative;
    width: 100%;
    height: 500px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
}}

.graph-container svg {{
    width: 100%;
    height: 100%;
}}

/* Requirements */
.req-list {{
    list-style: none;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.5rem;
}}

.req-list li {{
    padding: 0.5rem 0.75rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: var(--text-primary);
}}

.req-list .more {{
    color: var(--text-muted);
    font-style: italic;
}}

.no-req {{
    color: var(--text-muted);
    font-style: italic;
}}

/* Scrollbar */
::-webkit-scrollbar {{
    width: 10px;
    height: 10px;
}}

::-webkit-scrollbar-track {{
    background: var(--bg-primary);
}}

::-webkit-scrollbar-thumb {{
    background: var(--border);
    border-radius: 5px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--border-light);
}}

/* Responsive */
@media (max-width: 768px) {{
    .container {{
        padding: 0 1rem;
    }}
    
    h1 {{
        font-size: 2rem;
    }}
    
    .stats-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}
</style>
</head>
<body>

<!-- Header -->
<div class="header">
    <div class="container">
        <div class="header-content">
            <h1>{self.project_name}</h1>
            <p class="subtitle">Python Project Report</p>
            <p class="generated">Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>
</div>

<div class="container">

<!-- Stats -->
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">{len(files)}</div>
        <div class="stat-label">Files</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{total_lines:,}</div>
        <div class="stat-label">Lines</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{total_functions}</div>
        <div class="stat-label">Functions</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{total_classes}</div>
        <div class="stat-label">Classes</div>
    </div>
</div>

<!-- Dependencies -->
<div class="section">
    <h2>📦 Dependencies</h2>
    {req_list}
</div>

<!-- Execution Order -->
<div class="section">
    <h2>📋 Execution Order</h2>
    <p style="color: var(--text-secondary); margin-bottom: 1rem;">
        Files ordered by dependency — dependencies come first. 🎯 marks entry points.
    </p>
    <div class="exec-list">{exec_items}</div>
</div>

<!-- Dependency Graph -->
<div class="section">
    <h2>🔗 Dependency Graph</h2>
    <p style="color: var(--text-secondary); margin-bottom: 1rem;">
        Visual representation of file dependencies. Drag nodes to rearrange.
    </p>
    <div class="graph-container">
        <svg id="graph"></svg>
    </div>
</div>

<!-- File List -->
<div class="section">
    <h2>📄 Files</h2>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Lines</th>
                    <th>Functions</th>
                    <th>Classes</th>
                </tr>
            </thead>
            <tbody>{file_table_html}</tbody>
        </table>
    </div>
</div>

</div>

<script>
// ═══════════════════════════════════════════════════════════
// D3.js Force-Directed Graph
// ═══════════════════════════════════════════════════════════

const graphData = {graph_json};

const svg = d3.select("#graph");
const container = svg.node().parentElement;
const width = container.clientWidth;
const height = container.clientHeight;

svg.attr("viewBox", [0, 0, width, height]);

// Create nodes and links
const nodes = graphData.nodes.map(d => ({{...d}}));
const links = graphData.edges.map(d => ({{
    source: nodes.find(n => n.id === d.source),
    target: nodes.find(n => n.id === d.target),
}})).filter(d => d.source && d.target);

// Force simulation
const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(120))
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(30));

// Links
const link = svg.append("g")
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("stroke", "#444444")
    .attr("stroke-opacity", 0.6)
    .attr("stroke-width", 1.5);

// Nodes
const node = svg.append("g")
    .selectAll("g")
    .data(nodes)
    .join("g")
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

node.append("circle")
    .attr("r", d => Math.max(8, Math.min(20, 8 + d.lines / 50)))
    .attr("fill", "#58a6ff")
    .attr("stroke", "#1a1a1a")
    .attr("stroke-width", 2);

node.append("text")
    .text(d => d.label)
    .attr("x", 0)
    .attr("y", d => Math.max(8, Math.min(20, 8 + d.lines / 50)) + 15)
    .attr("text-anchor", "middle")
    .attr("fill", "#b0b0b0")
    .attr("font-size", "11px")
    .attr("font-family", "JetBrains Mono, monospace");

// Update positions
simulation.on("tick", () => {{
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
}});

function dragstarted(event) {{
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
}}

function dragged(event) {{
    event.subject.fx = event.x;
    event.subject.fy = event.y;
}}

function dragended(event) {{
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
}}
</script>

</body>
</html>"""


def generate_html_report(project_data: Dict[str, Any], output_path: str) -> str:
    """Standalone function to generate HTML report."""
    visualizer = HTMLVisualizer(project_data)
    return visualizer.generate(output_path)
