"""
Authentication setup for GCP private packages in Streamlit Cloud.
This module handles authentication for pip to access private repositories.
"""

import os
import json
import tempfile
import subprocess
import sys
from pathlib import Path
import streamlit as st


def setup_gcp_authentication():
    """Set up GCP authentication for accessing private packages."""
    
    # Get service account credentials
    service_account_info = None
    
    # Try Streamlit secrets first (preferred for Streamlit Cloud)
    try:
        if hasattr(st, 'secrets') and "gcp_service_account" in st.secrets:
            service_account_info = dict(st.secrets["gcp_service_account"])
    except Exception:
        pass
    
    # Try environment variable as fallback
    if not service_account_info and "GCP_SERVICE_ACCOUNT" in os.environ:
        try:
            service_account_info = json.loads(os.environ["GCP_SERVICE_ACCOUNT"])
        except json.JSONDecodeError:
            pass
    
    if not service_account_info:
        return None
    
    # Create temporary service account file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(service_account_info, f)
        credentials_file = f.name
    
    # Set Google Application Credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
    
    try:
        # Get access token using google-auth
        from google.auth import default
        from google.auth.transport.requests import Request
        
        credentials, project = default()
        credentials.refresh(Request())
        
        return credentials.token
        
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None
    
    finally:
        # Clean up temporary file
        if os.path.exists(credentials_file):
            os.unlink(credentials_file)


def configure_pip_authentication():
    """Configure pip to use GCP authentication token."""
    
    # Get authentication token
    token = setup_gcp_authentication()
    
    if not token:
        return False
    
    # Create pip configuration directory
    pip_config_dir = Path.home() / ".pip"
    pip_config_dir.mkdir(exist_ok=True)
    
    # Create pip configuration file
    pip_config_file = pip_config_dir / "pip.conf"
    
    # Configuration content
    config_content = f"""[global]
trusted-host = europe-west4-python.pkg.dev
extra-index-url = https://oauth2accesstoken:{token}@europe-west4-python.pkg.dev/gpu-reservation-sarvam/sarvam-python-ci/simple/
"""
    
    # Write configuration
    with open(pip_config_file, "w") as f:
        f.write(config_content)
    
    return True


def install_private_packages():
    """Install private packages using pip with authentication."""
    
    # Set up authentication
    if not configure_pip_authentication():
        return False
    
    # Private packages to install
    private_packages = [
        "sarvam-datatypes==0.4.20",
        "sarvam-stream==0.3.9",
        "sarvam-agents-sdk==0.2.176"
    ]
    
    # Install each private package
    for package in private_packages:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
            
            print(f"✓ Successfully installed {package}")
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
            return False
    
    return True


def check_private_packages():
    """Check if private packages are already installed."""
    
    try:
        import sarvam_datatypes
        import sarvam_stream
        import sarvam_agents_sdk
        return True
    except ImportError:
        return False


def ensure_authentication():
    """Ensure authentication is set up and packages are available."""
    
    # Check if packages are already available
    if check_private_packages():
        return True
    
    # Install packages if not available
    print("Setting up authentication for private packages...")
    
    if install_private_packages():
        print("✓ Private packages installed successfully!")
        return True
    else:
        print("✗ Failed to install private packages")
        return False


# Auto-setup authentication when module is imported
if __name__ != "__main__":
    ensure_authentication() 