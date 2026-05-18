#!/usr/bin/env python3
"""
PHASE 18: Email Alerting via SMTP
Sends alerts for critical system events.
"""

import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

class OmegaMailAlert:
    def __init__(self, config_path: Optional[str] = None):
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
        else:
            config = {
                "smtp_host": os.getenv("SMTP_HOST", "localhost"),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "smtp_user": os.getenv("SMTP_USER", ""),
                "smtp_password": os.getenv("SMTP_PASSWORD", ""),
                "from_addr": os.getenv("ALERT_FROM", "omega@localhost"),
                "to_addrs": os.getenv("ALERT_TO", "").split(","),
                "use_tls": os.getenv("SMTP_TLS", "true").lower() == "true"
            }
        
        self.smtp_host = config["smtp_host"]
        self.smtp_port = config["smtp_port"]
        self.smtp_user = config["smtp_user"]
        self.smtp_password = config["smtp_password"]
        self.from_addr = config["from_addr"]
        self.to_addrs = [a.strip() for a in config["to_addrs"] if a.strip()]
        self.use_tls = config["use_tls"]
    
    def send_alert(self, subject: str, body: str, priority: str = "normal") -> bool:
        """Send an email alert."""
        if not self.to_addrs:
            print("No recipients configured, skipping alert")
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[OMEGA-{priority.upper()}] {subject}"
            msg["From"] = self.from_addr
            msg["To"] = ", ".join(self.to_addrs)
            msg["Date"] = datetime.now().isoformat()
            
            html_body = self._format_html(subject, body, priority)
            msg.attach(MIMEText(body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                
                server.sendmail(self.from_addr, self.to_addrs, msg.as_string())
            
            return True
            
        except Exception as e:
            print(f"Failed to send alert: {e}")
            return False
    
    def _format_html(self, subject: str, body: str, priority: str) -> str:
        """Format alert as HTML."""
        colors = {
            "critical": "#ff4444",
            "high": "#ff8800",
            "normal": "#4488ff",
            "low": "#44bb44"
        }
        color = colors.get(priority.lower(), "#4488ff")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: {color}; color: white; padding: 15px; border-radius: 5px; }}
                .content {{ padding: 20px; background: #f5f5f5; border-radius: 5px; margin-top: 10px; }}
                .footer {{ color: #888; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>OMEGA Alert: {subject}</h2>
            </div>
            <div class="content">
                <pre>{body}</pre>
            </div>
            <div class="footer">
                Generated: {datetime.now().isoformat()}<br>
                System: Paradise Stack / OMEGA-CODE
            </div>
        </body>
        </html>
        """
    
    def alert_recursion_overload(self, current_depth: int, max_depth: int) -> bool:
        """Alert when recursion exceeds threshold (>50)."""
        return self.send_alert(
            subject="Recursion Overload Detected",
            body=f"Recursion depth {current_depth} exceeds threshold of {max_depth}.",
            priority="critical"
        )
    
    def alert_unauthorized_access(self, user: str, ip: str, action: str) -> bool:
        """Alert on unauthorized access attempts."""
        return self.send_alert(
            subject="Unauthorized Access Attempt",
            body=f"User: {user}\nIP: {ip}\nAction: {action}",
            priority="high"
        )
    
    def alert_memory_pressure(self, usage_percent: float) -> bool:
        """Alert when memory usage exceeds 90%."""
        return self.send_alert(
            subject="Memory Pressure Warning",
            body=f"Memory usage at {usage_percent:.1f}% - approaching limit.",
            priority="critical" if usage_percent > 95 else "high"
        )
    
    def alert_system_restart(self, reason: str) -> bool:
        """Alert on system restart."""
        return self.send_alert(
            subject="System Restart",
            body=f"OMEGA system restarted. Reason: {reason}",
            priority="normal"
        )


if __name__ == "__main__":
    import sys
    
    alert = OmegaMailAlert()
    
    if len(sys.argv) >= 2:
        command = sys.argv[1]
        
        if command == "test":
            alert.send_alert("Test Alert", "This is a test alert from OMEGA.", "normal")
        
        elif command == "recursion":
            alert.alert_recursion_overload(55, 50)
        
        elif command == "unauthorized":
            alert.alert_unauthorized_access("unknown", "192.168.1.100", "sudo")
        
        elif command == "memory":
            alert.alert_memory_pressure(92.5)
    
    print("Alert types: test, recursion, unauthorized, memory")
