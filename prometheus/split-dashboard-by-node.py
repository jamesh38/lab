#!/usr/bin/env python3
"""
Split Grafana dashboard into separate rows for each Kubernetes node.
This script takes an existing dashboard and duplicates all panels,
creating one row for 'opti' node and one row for 'thinkpad' node.
"""

import json
import sys
import copy

def add_node_filter_to_query(query, node_name):
    """Add node label filter to a Prometheus query."""
    expr = query.get('expr', '')
    if not expr:
        return query

    # Skip if already has a node filter
    if 'kubernetes_io_hostname' in expr or f'instance=~".*{node_name}.*"' in expr:
        return query

    # Add node filter based on common label patterns
    # node-exporter uses 'kubernetes_io_hostname' label
    if '{' in expr:
        # Insert filter into existing label matcher
        expr = expr.replace('{', f'{{kubernetes_io_hostname="{node_name}",', 1)
    else:
        # Add label matcher if none exists
        metric_name = expr.split('[')[0].split('(')[-1].strip()
        expr = expr.replace(metric_name, f'{metric_name}{{kubernetes_io_hostname="{node_name}"}}', 1)

    query['expr'] = expr
    return query

def create_row_panel(title, y_pos):
    """Create a row separator panel."""
    return {
        "collapsed": False,
        "gridPos": {
            "h": 1,
            "w": 24,
            "x": 0,
            "y": y_pos
        },
        "id": None,  # Will be assigned by Grafana
        "panels": [],
        "title": title,
        "type": "row"
    }

def split_dashboard_by_nodes(dashboard, nodes):
    """Split dashboard panels into separate rows for each node."""
    # Get existing panels (excluding rows)
    existing_panels = [p for p in dashboard.get('panels', []) if p.get('type') != 'row']

    # Create new panels list with rows and node-specific panels
    new_panels = []
    current_y = 0

    for node_name in nodes:
        # Add row separator
        row_panel = create_row_panel(f"Node: {node_name}", current_y)
        new_panels.append(row_panel)
        current_y += 1

        # Duplicate all panels for this node
        for panel in existing_panels:
            new_panel = copy.deepcopy(panel)

            # Update panel title to include node name
            original_title = new_panel.get('title', 'Panel')
            new_panel['title'] = f"{original_title} ({node_name})"

            # Update gridPos
            old_grid = new_panel.get('gridPos', {})
            new_panel['gridPos'] = {
                'h': old_grid.get('h', 8),
                'w': old_grid.get('w', 12),
                'x': old_grid.get('x', 0),
                'y': current_y + old_grid.get('y', 0)
            }

            # Update queries to filter by node
            if 'targets' in new_panel:
                for target in new_panel['targets']:
                    add_node_filter_to_query(target, node_name)

            new_panels.append(new_panel)

        # Calculate max Y position for next row
        if existing_panels:
            max_y = max(p.get('gridPos', {}).get('y', 0) + p.get('gridPos', {}).get('h', 8)
                       for p in existing_panels)
            current_y += max_y + 1

    dashboard['panels'] = new_panels
    return dashboard

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 split-dashboard-by-node.py <dashboard.json>")
        sys.exit(1)

    dashboard_file = sys.argv[1]

    # Read dashboard
    with open(dashboard_file, 'r') as f:
        dashboard = json.load(f)

    # Define your nodes
    nodes = ['opti', 'thinkpad']

    # Split dashboard
    new_dashboard = split_dashboard_by_nodes(dashboard, nodes)

    # Update dashboard title
    old_title = new_dashboard.get('title', 'Dashboard')
    new_dashboard['title'] = f"{old_title} (Multi-Node)"

    # Write output
    output_file = dashboard_file.replace('.json', '-multi-node.json')
    with open(output_file, 'w') as f:
        json.dump(new_dashboard, f, indent=2)

    print(f"Created multi-node dashboard: {output_file}")
    print(f"Nodes: {', '.join(nodes)}")
    print(f"Total panels: {len(new_dashboard['panels'])}")

if __name__ == '__main__':
    main()
