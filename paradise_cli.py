"""
Paradise Stack CLI Interface
The face of an perpetually learning, never-stopping AI organization.
"""

import os
import sys
import json
from pathlib import Path
from cognition.continuous_intelligence import (
    initialize_evolution,
    evolve_with_scan,
    ParadiseStackPersona
)

INTELLIGENCE_DIR = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS\\intelligence")

class ParadiseStackCLI:
    """Interactive CLI for Paradise Stack v2.0"""
    
    BANNER = """
    +====================================================================+
    |                                                                    |
    |   PARADISE STACK v2.0 - Autonomous AI Organization                 |
    |   "Excellent - Adaptable - Robotically Accurate - Never Stops"    |
    |                                                                    |
    +====================================================================+
    """
    
    def __init__(self):
        self.engine = initialize_evolution()
        self.state = self.engine.get_evolved_state()
    
    def display_banner(self):
        """Display the Paradise Stack banner."""
        print(self.BANNER)
        self._display_identity()
    
    def _display_identity(self):
        """Display current identity and state."""
        level = self.state['evolution_level']
        bar = "=" * level + "-" * (10 - level)
        print(f"  Evolution Level: [{bar}] ({level}/10)")
        print(f"  Skills Integrated: {self.state['skills_integrated']}")
        print(f"  Patterns Mastered: {self.state['patterns_mastered']}")
        print(f"  Knowledge Age: {self.state['knowledge_age_days']} days")
        print()
    
    def display_capabilities(self):
        """Show current capabilities."""
        print("\n  CAPABILITIES")
        print("  " + "-" * 50)
        for cap in ParadiseStackPersona.get_current_capabilities():
            print(f"    [+] {cap}")
        
        if self.state['top_patterns']:
            print("\n  TOP PATTERNS")
            print("  " + "-" * 50)
            for pattern in self.state['top_patterns'][:5]:
                print(f"    -> {pattern['pattern'][:40]} ({pattern['usage_count']} uses)")
        print()
    
    def display_status(self):
        """Display detailed system status."""
        cache_path = INTELLIGENCE_DIR / "cache" / "intelligence_cache.json"
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                cache = json.load(f)
            print("\n  SCAN STATUS")
            print("  " + "-" * 50)
            print(f"    Last Scan: {cache.get('last_scan', 'Never')}")
            print(f"    Next Due: {cache.get('next_scan_due', 'Not scheduled')}")
        
        suggestions = self.engine.suggest_improvements()
        if suggestions:
            print("\n  RECOMMENDATIONS")
            print("  " + "-" * 50)
            for sug in suggestions[:5]:
                print(f"    -> {sug.get('recommendation', 'Unknown')}")
        print()
    
    def run_intelligence_scan(self):
        """Run the monthly intelligence scan."""
        print("\n  Starting GitHub Intelligence Scan...")
        print("  " + "-" * 50)
        
        try:
            results = evolve_with_scan()
            print(f"  [OK] Patterns added: {results['evolution_results']['patterns_extracted']}")
            print(f"  [OK] Skills integrated: {results['evolution_results']['knowledge_added']}")
            print(f"  [OK] Evolution level: {results['current_state']['evolution_level']}/10")
            self.state = results['current_state']
        except Exception as e:
            print(f"  [FAIL] Scan failed: {e}")
        
        print()
    
    def interact_mode(self):
        """Interactive mode for direct conversation."""
        print("\n  INTERACTIVE MODE")
        print("  " + "─" * 50)
        print("  Type 'exit' to return, 'scan' to run intelligence scan")
        print("  'status' for details, 'capabilities' for current skills")
        print()
        
        while True:
            try:
                user_input = input("  You: ").strip()
                
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'scan':
                    self.run_intelligence_scan()
                elif user_input.lower() == 'status':
                    self.display_status()
                elif user_input.lower() == 'capabilities':
                    self.display_capabilities()
                elif user_input:
                    self.engine.evolve_from_interaction({
                        "type": "user_query",
                        "content": user_input,
                        "outcome": "processed"
                    })
                    print("  System: Learned from your query. Pattern recorded.")
                    print(f"  Current patterns tracked: {len(self.engine.master_patterns)}")
                else:
                    print("  System: I listen, I learn. Ask me anything.")
            except KeyboardInterrupt:
                print("\n\n  System: Session ended. Knowledge preserved.")
                break
            except Exception as e:
                print(f"  Error: {e}")
        
        print()
    
    def show_menu(self):
        """Display main menu."""
        print("\n  MAIN MENU")
        print("  " + "─" * 50)
        print("    1. View Capabilities")
        print("    2. System Status")
        print("    3. Run Intelligence Scan")
        print("    4. Interactive Mode")
        print("    5. About Paradise Stack")
        print("    6. Exit")
        print()
        
        choice = input("  Select (1-6): ").strip()
        
        if choice == '1':
            self.display_capabilities()
        elif choice == '2':
            self.display_status()
        elif choice == '3':
            self.run_intelligence_scan()
        elif choice == '4':
            self.interact_mode()
        elif choice == '5':
            print(f"\n  {ParadiseStackPersona.IDENTITY}")
        elif choice == '6':
            print("\n  Paradise Stack: Until next time. Knowledge preserved.\n")
            sys.exit(0)
        
        self.show_menu()
    
    def run(self):
        """Run the CLI interface."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.display_banner()
        self.show_menu()


def main():
    """Entry point."""
    cli = ParadiseStackCLI()
    cli.run()


if __name__ == "__main__":
    main()
