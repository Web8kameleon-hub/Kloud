#!/usr/bin/env python3
"""
Curiosity Ocean Chat Client
Simple CLI to chat with Ocean Curiosity AI
"""

from typing import Optional

import requests

# Configuration
OCEAN_URL = "http://46.62.210.251:8030"  # Change to your server
OCEAN_API = f"{OCEAN_URL}/api/v1/query"
TIMEOUT = 300


def chat_with_ocean(query: str, context: Optional[str] = None) -> str:
    """Send a query to Curiosity Ocean and get response"""
    try:
        payload = {"query": query, **({"context": context} if context else {})}

        print("\n🌊 Curiosity Ocean thinking...", end="", flush=True)
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


def main():
    """Main chat loop"""
    print("=" * 60)
    print("🌊 Welcome to Curiosity Ocean Chat")
    print("=" * 60)
    print("Type your questions and press Enter")
    print("Type 'exit' to quit")
    print("Type 'help' for available commands")
    print("=" * 60)

    while True:
        try:
            # Get user input
            query = input("\n🤔 You: ").strip()

            if not query:
                continue

            # Handle commands
            if query.lower() == "exit":
                print("\n👋 Thank you for exploring Curiosity Ocean!")
                break

            if query.lower() == "help":
                print("\n📚 Commands:")
                print("  exit     - Leave Ocean")
                print("  help     - Show this message")
                print("  clear    - Clear screen")
                print("  status   - Check Ocean status")
                continue

            if query.lower() == "clear":
                print("\033[2J\033[H")  # Clear screen
                continue

            if query.lower() == "status":
                try:
                    resp = requests.get(f"{OCEAN_URL}/health", timeout=5)
                    if resp.status_code == 200:
                        print(f"✅ Ocean is healthy: {resp.json()}")
                    else:
                        print(f"⚠️ Ocean status: {resp.status_code}")
                except requests.RequestException:
                    print("❌ Cannot reach Ocean")
                continue

            # Send query to Ocean
            response = chat_with_ocean(query)
            print(f"\n🌊 Ocean: {response}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
