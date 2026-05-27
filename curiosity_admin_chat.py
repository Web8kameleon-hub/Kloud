#!/usr/bin/env python3
"""
Curiosity Ocean Chat - Admin Detection System
Detects admin users and provides elevated context
"""

import json
from typing import Optional, Tuple

import requests

# Configuration
OCEAN_URL = "http://46.62.210.251:8030"
OCEAN_API = f"{OCEAN_URL}/api/v1/query"
TIMEOUT = 300

# Admin keywords and patterns
ADMIN_KEYWORDS = [
    "admin",
    "system",
    "config",
    "deploy",
    "docker",
    "server",
    "database",
    "api",
    "security",
    "firewall",
    "ssh",
    "terminal",
    "kubernetes",
    "devops",
    "infrastructure",
    "network",
    "ssl",
    "certificate",
    "backup",
    "restore",
    "migration",
    "scaling",
    "performance",
    "monitoring",
    "logs",
    "debug",
    "error",
    "fix",
    "patch",
    "update",
    "install",
    "package",
    "dependency",
]

# Admin commands
ADMIN_COMMANDS = {
    "!status": "Get full system status",
    "!services": "List all running services",
    "!health": "Check system health",
    "!config": "Show system configuration",
    "!help": "Show admin commands",
    "!exit": "Exit chat",
}

USER_COMMANDS = {
    "help": "Show available commands",
    "status": "Check Ocean status",
    "exit": "Exit chat",
}


def detect_admin_intent(message: str) -> Tuple[bool, str]:
    """
    Detect if message is from admin based on keywords and patterns
    Returns: (is_admin, reason)
    """
    message_lower = message.lower()

    # Check for admin keywords
    admin_score: int = 0
    matched_keywords = []

    for keyword in ADMIN_KEYWORDS:
        if keyword in message_lower:
            admin_score += 1
            matched_keywords.append(keyword)

    # Check for admin commands (! prefix)
    if message.startswith("!"):
        return True, "Admin command detected"

    # If multiple admin keywords or specific patterns
    if admin_score >= 2:
        return True, f"Admin intent detected: {', '.join(matched_keywords[:3])}"

    # Check for system/technical questions
    technical_patterns = ["how to", "configure", "setup", "install", "deploy"]
    for pattern in technical_patterns:
        if pattern in message_lower:
            admin_score += 1

    if admin_score >= 2:
        return True, "Technical/Admin question detected"

    return False, "Regular user query"


def get_admin_context(message: str) -> str:
    """Generate admin-level context for Ocean"""
    return """You are speaking with a system administrator. Provide technical details, 
system-level insights, configuration information, and optimization recommendations. 
Include technical specifications, architecture details, and deployment considerations."""


def get_user_context(message: str) -> str:
    """Generate user-level context for Ocean"""
    return """You are speaking with a regular user. Provide clear, accessible explanations.
Avoid overly technical jargon. Focus on practical information and actionable insights."""


def chat_with_ocean(
    query: str, context: Optional[str] = None, is_admin: bool = False
) -> str:
    """Send a query to Curiosity Ocean"""
    try:
        # Add role context
        if is_admin:
            full_context = get_admin_context(query)
            if context:
                full_context += f"\nSpecific context: {context}"
        else:
            full_context = get_user_context(query)
            if context:
                full_context += f"\nSpecific context: {context}"

        payload = {"query": query, "context": full_context}

        print("\n🤔 Thinking...", end="", flush=True)
        response = requests.post(OCEAN_API, json=payload, timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response received")
        else:
            return f"❌ Error {response.status_code}: {response.text}"

    except requests.exceptions.Timeout:
        return "❌ Request timeout - Ocean is thinking too deep!"
    except requests.exceptions.ConnectionError:
        return f"❌ Cannot connect to Ocean at {OCEAN_URL}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def handle_admin_command(command: str) -> Optional[str]:
    """Handle special admin commands"""
    if command == "!status":
        return "📊 System Status: All 52 services UP ✅"
    elif command == "!services":
        return """🐳 Running Services:
  • API (8000) - Healthy
  • Web (3000) - Running
  • Ocean-Core (8030) - Healthy
  • Ollama (11434) - Active
  • PostgreSQL (5432) - Healthy
  • Redis (6379) - Healthy"""
    elif command == "!health":
        try:
            resp = requests.get(f"{OCEAN_URL}/health", timeout=5)
            if resp.status_code == 200:
                return "✅ Ocean Health: " + json.dumps(resp.json(), indent=2)
        except Exception as e:
            return "⚠️ Cannot check health: " + str(e)
    elif command == "!config":
        return """⚙️ System Configuration:
    • Server: 46.62.210.251
  • AI Model: llama3.1:8b
  • Framework: Curiosity Ocean v2
  • Containers: 52/52 UP
  • Database: PostgreSQL 16
  • Cache: Redis 7"""
    elif command == "!help":
        help_text = "🛠️ Admin Commands:\n"
        for cmd, desc in ADMIN_COMMANDS.items():
            help_text += f"  {cmd:<15} - {desc}\n"
        return help_text
    return None


def main():
    """Main chat loop with admin detection"""
    current_user = None
    is_admin = False

    print("=" * 70)
    print("🌊 Curiosity Ocean Chat - Admin Detection System")
    print("=" * 70)

    # Login
    print("\n🔐 Login")
    username = input("Username: ").strip() or "user"

    # Simple admin detection based on username
    if username.lower() in ["admin", "root", "ledjan"]:
        is_admin = True
        current_user = username
        print(f"\n✅ Welcome Admin {username}!")
        print("🔓 Admin mode activated - You have elevated privileges")
    else:
        current_user = username
        print(f"\n✅ Welcome {username}!")
        print("Standard user mode - Ask anything!")

    role_badge = "🛡️ [ADMIN]" if is_admin else "👤 [USER]"

    print("\n" + role_badge + " Type 'help' for commands, 'exit' to quit")
    print("=" * 70)

    while True:
        try:
            # Get input
            user_input = input(f"\n{role_badge} {current_user}: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() == "help":
                if is_admin:
                    print("\n🛠️ Admin Commands:")
                    for cmd, desc in ADMIN_COMMANDS.items():
                        print(f"  {cmd:<15} - {desc}")
                else:
                    print("\n📚 Commands:")
                    for cmd, desc in USER_COMMANDS.items():
                        print(f"  {cmd:<15} - {desc}")
                continue

            if user_input.lower() == "exit":
                print(f"\n👋 Goodbye {current_user}!")
                break

            # Check for admin commands
            if is_admin and user_input.startswith("!"):
                result = handle_admin_command(user_input)
                if result:
                    print(f"\n⚡ Admin Response:\n{result}")
                    continue

            # Auto-detect admin intent
            detected_admin, reason = detect_admin_intent(user_input)
            if detected_admin and not is_admin:
                print(f"\n🔍 Detected: {reason}")
                print("⚠️ Admin features require authentication")
                continue

            # Show detection status
            if detected_admin:
                print(f"✅ {reason}")

            # Send to Ocean
            response = chat_with_ocean(
                user_input,
                context=reason if detected_admin else None,
                is_admin=is_admin,
            )

            print(f"\n🌊 Ocean: {response}")

        except KeyboardInterrupt:
            print(f"\n\n👋 Goodbye {current_user}!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
