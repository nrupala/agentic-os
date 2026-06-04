# SPDX-License-Identifier: MIT OR Apache-2.0
import sqlite3

class MetaCognition:
    def __init__(self, db_path):
        self.db_path = db_path

    def analyze_failure_patterns(self):
        """Extracts patterns from the last 5 failures to inform the Architect."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT logs FROM state WHERE status = 'FAIL' ORDER BY id DESC LIMIT 5")
        failures = cursor.fetchall()
        conn.close()

        if not failures:
            return "No previous logic breaches. Apply standard best practices."

        summary = "\n".join([f"- {f[0][:150]}..." for f in failures])
        return f"CRITICAL FAILURE ANALYSIS:\n{summary}"

    def derive_constraints(self, patterns):
        """Generates 'Hard Thinking Rules' that the LLM must follow to proceed."""
        # This acts as an automated 'System Instruction' update
        return [
            "CONSTRAINT_ALPHA: Use absolute pathing for all file operations.",
            "CONSTRAINT_BETA: Implement explicit retry logic for third-party API calls.",
            "CONSTRAINT_GAMMA: Strictly type all function signatures."
        ]
