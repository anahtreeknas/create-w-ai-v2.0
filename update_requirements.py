#!/usr/bin/env python3
"""
Script to update requirements.txt from Poetry, excluding private packages.
This helps maintain compatibility with Streamlit Cloud while using Poetry.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✓ {description}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None


def update_requirements():
    """Update requirements.txt from Poetry, excluding private packages."""
    
    print("Updating requirements.txt from Poetry...")
    print("=" * 50)
    
    # Export from Poetry
    output = run_command(
        "poetry export -f requirements.txt --output requirements_temp.txt --without-hashes",
        "Exporting from Poetry"
    )
    
    if output is None:
        return False
    
    # Read the temporary file
    temp_file = Path("requirements_temp.txt")
    if not temp_file.exists():
        print("✗ Temporary requirements file not found")
        return False
    
    # Process the file to remove private packages
    with open(temp_file, 'r') as f:
        lines = f.readlines()
    
    # Filter out private packages and the extra-index-url
    filtered_lines = []
    private_packages = ["sarvam-", "sarvam_"]
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Skip extra-index-url lines (will be handled at runtime)
        if line.startswith("--extra-index-url"):
            continue
        
        # Skip private packages
        if any(pkg in line for pkg in private_packages):
            print(f"Skipping private package: {line}")
            continue
        
        filtered_lines.append(line + "\n")
    
    # Write the filtered requirements
    with open("requirements.txt", 'w') as f:
        f.writelines(filtered_lines)
    
    # Clean up temp file
    temp_file.unlink()
    
    print(f"✓ Updated requirements.txt with {len(filtered_lines)} packages")
    print("✓ Excluded private packages (will be installed at runtime)")
    
    return True


def main():
    """Main function."""
    
    # Check if we're in a Poetry project
    if not Path("pyproject.toml").exists():
        print("✗ No pyproject.toml found. Are you in a Poetry project?")
        sys.exit(1)
    
    # Update requirements
    if update_requirements():
        print("\n" + "=" * 50)
        print("✓ Requirements updated successfully!")
        print("\nNext steps:")
        print("1. Review the updated requirements.txt")
        print("2. Commit the changes to your repository")
        print("3. Deploy to Streamlit Cloud")
        print("4. Make sure GCP credentials are configured in Streamlit secrets")
    else:
        print("\n✗ Failed to update requirements")
        sys.exit(1)


if __name__ == "__main__":
    main() 