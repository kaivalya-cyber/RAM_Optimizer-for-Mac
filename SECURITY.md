# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in RAM Optimizer, please report it responsibly.

**Do not open a public issue.** Instead, please contact the project maintainer via [GitHub](https://github.com/kaivalya-cyber) with details.

We aim to acknowledge reports within 48 hours and provide a timeline for a fix within 5 business days.

## Scope

Security concerns include but are not limited to:

- Unauthorized privilege escalation (the tool requires sudo for purge/cache operations)
- Arbitrary command execution via cache-clearing paths
- Sensitive data exposure in logs or configuration files
- Path traversal vulnerabilities in file operations

## Best Practices for Users

- Always review what caches will be cleared before running optimization
- The tool writes logs to `~/.ram_optimizer.log` and settings to `~/.ram_optimizer_config.json`
- These files may contain system information; restrict access if needed
- The `sudo purge` command requires your administrator password — never share it

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Acknowledgments

We appreciate responsible disclosure and will credit researchers who report valid vulnerabilities (with permission).
