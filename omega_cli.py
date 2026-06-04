#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
OMEGA Complete CLI
==================
Unified command-line interface for the entire agentic-OS system.

Usage:
    python omega_cli.py --goal "Build a REST API"
    python omega_cli.py --interactive
    python omega_cli.py --status
"""

import sys
import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "engine"))

from omega_codex import OmegaCodex
from omega_seamless_service import OmegaSeamlessService


def print_banner():
    print("""
========================================================
       OMEGA CODEX - Unified Agent System
                 Version 1.0.0
========================================================
    """)


def cmd_status(args):
    """Show system status."""
    print_banner()
    
    codex = OmegaCodex()
    status = codex.get_status()
    
    print("\n=== OMEGA CODEX STATUS ===")
    print(f"Version: {status['version']}")
    print(f"Subsystems: {len(status['subsystems'])}")
    print(f"Requests Processed: {status['requests_processed']}")
    
    print("\n=== AVAILABLE SUBSYSTEMS ===")
    for sub in status['subsystems']:
        print(f"  + {sub}")
    
    # Show seamless service status
    print("\n=== SEAMLESS SERVICE ===")
    try:
        seamless = OmegaSeamlessService()
        s_status = seamless.get_status()
        print(f"Status: {s_status.status}")
        print(f"Components: {len(s_status.components)}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_goal(args):
    """Process a user goal."""
    print_banner()
    print(f"\n>>> GOAL: {args.goal}\n")
    
    codex = OmegaCodex()
    result = codex.process(args.goal)
    
    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Request ID: {result.request_id}")
    print(f"Success: {result.success}")
    print(f"Execution Time: {result.execution_time_ms}ms")
    
    print("\n--- METRICS ---")
    for k, v in result.metrics.items():
        print(f"  {k}: {v}")
    
    if result.outputs:
        print("\n--- OUTPUTS ---")
        for k, v in result.outputs.items():
            if isinstance(v, dict):
                print(f"  {k}: {json.dumps(v)[:100]}...")
            else:
                print(f"  {k}: {v}")
    
    if result.errors:
        print("\n--- ERRORS ---")
        for e in result.errors:
            print(f"  - {e}")
    
    print()


def cmd_context(args):
    """Get context for a query."""
    codex = OmegaCodex()
    seamless = codex.get_subsystem('seamless')
    
    if seamless:
        ctx = seamless.get_full_context(args.query if hasattr(args, 'query') else None)
        print(json.dumps(ctx, indent=2))
    else:
        print("Seamless service not available")


def cmd_search(args):
    """Search code."""
    codex = OmegaCodex()
    results = codex.process(f"Search for: {args.query}")
    
    print(f"\nSearch results for: {args.query}")
    print("-" * 40)
    
    for output_name, output_data in results.outputs.items():
        print(f"{output_name}: {output_data}")


def cmd_interactive(args):
    """Interactive mode."""
    print_banner()
    print("\nInteractive Mode (Ctrl+C to exit)")
    print("Type your goals and press Enter\n")
    
    codex = OmegaCodex()
    
    while True:
        try:
            user_input = input("\n> ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            result = codex.process(user_input)
            
            print(f"\n  + Success: {result.success}")
            print(f"  + Time: {result.execution_time_ms}ms")
            print(f"  + Tasks: {result.metrics['successful_tasks']}/{result.metrics['total_tasks']}")
            
            if result.errors:
                print(f"  - Errors: {len(result.errors)}")
                for e in result.errors[:2]:
                    print(f"      - {e[:60]}")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def cmd_serve(args):
    """Start as API server."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    codex = OmegaCodex()
    
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length).decode()
            data = json.loads(body)
            
            result = codex.process(data.get('goal', ''))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': result.success,
                'outputs': result.outputs,
                'errors': result.errors,
                'metrics': result.metrics
            }).encode())
        
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(codex.get_status()).encode())
        
        def log_message(self, format, *args):
            pass  # Suppress logging
    
    print(f"Starting OMEGA API Server on http://localhost:{args.port}")
    server = HTTPServer(('0.0.0.0', args.port), Handler)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(
        description="OMEGA Complete CLI - Unified Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Goal command
    goal_parser = subparsers.add_parser('goal', help='Process a user goal')
    goal_parser.add_argument('--goal', type=str, required=True, help='Your goal')
    goal_parser.add_argument('--max-iters', type=int, default=5, help='Max iterations')
    
    # Context command
    ctx_parser = subparsers.add_parser('context', help='Get code context')
    ctx_parser.add_argument('query', nargs='?', default=None, help='Optional query')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search code')
    search_parser.add_argument('query', type=str, help='Search query')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Interactive mode')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start API server')
    serve_parser.add_argument('--port', type=int, default=8765, help='Port number')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        cmd_status(args)
    elif args.command == 'goal':
        cmd_goal(args)
    elif args.command == 'context':
        cmd_context(args)
    elif args.command == 'search':
        cmd_search(args)
    elif args.command == 'interactive':
        cmd_interactive(args)
    elif args.command == 'serve':
        cmd_serve(args)
    else:
        # Default: show status
        cmd_status(argparse.Namespace())


if __name__ == "__main__":
    main()