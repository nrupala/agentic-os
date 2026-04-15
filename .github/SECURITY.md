# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within agentic-OS, please report it responsibly.

### How to Report

1. **Do NOT** create a public GitHub issue for security vulnerabilities
2. Send a private vulnerability report to the maintainers
3. Include the following information:
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/commit/direct line)
   - Any special configuration required to reproduce the issue
   - Step-by-step instructions to reproduce
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue

### What to Expect

- Acknowledgment of your report within 48 hours
- Regular updates on the progress
- Credit for the discovery (unless you prefer to remain anonymous)

## Security Features

agentic-OS includes the following security measures:

- **AES-256-GCM Encryption**: All sensitive data encrypted at rest
- **RBAC Access Control**: Role-based permissions
- **Audit Logging**: Complete trail of all operations
- **Input Validation**: Sanitization of all user inputs
- **Dependency Scanning**: Automated vulnerability detection

## Security Scanning

This project uses:
- GitHub Code Scanning (CodeQL)
- Dependency Review
- Secret Scanning
- Bandit SAST scanning in CI

## Best Practices

When using agentic-OS:

1. **Never commit secrets** to the repository
2. **Use environment variables** for sensitive configuration
3. **Regularly update** dependencies to get security patches
4. **Review audit logs** for suspicious activity
5. **Follow least privilege** when configuring access controls
