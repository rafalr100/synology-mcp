# Example prompts

Natural-language prompts to use once the `synology` MCP server is connected.

## Overview & dashboards
- "Give me an overview of my NAS."
- "Build a dashboard for my Synology."
- "Show a storage-focused dashboard with disk health."
- "Dashboard of Docker containers and virtual machines."

## Health & monitoring
- "How's my NAS doing right now — CPU, RAM, temperature?"
- "Is the system healthy? Any reboot required?"
- "What are the top processes by memory?"
- "Who is connected to the NAS right now?"

## Storage
- "How full are my volumes?"
- "Are all disks healthy and what are their temperatures?"
- "Show my storage pools and scrubbing status."

## Files
- "List the files in /home."
- "Search /home for *.pdf."
- "How big is the /docker folder?"
- "Create a public share link for /home/report.pdf."

## Apps & updates
- "Is a DSM update available?"
- "List installed packages that are running."
- "Which Docker images have updates available?"
- "Show running containers and restart homeassistant." (will ask to confirm)
- "List my virtual machines and their state."
- "Show my Hyper Backup tasks and when they last ran."

## Administration
- "List users and which ones have 2FA enabled."
- "Are SSH and SMB enabled?"
- "What's my DDNS hostname and external IP?"
- "When do my TLS certificates expire?"
- "Show the last 10 system log entries and the security scan status."
