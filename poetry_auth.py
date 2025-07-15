"""
Poetry authentication handler for GCP private packages in Streamlit Cloud.
This sets up authentication for Poetry to access private repositories.
"""

import os
import json
import tempfile
import subprocess
import streamlit as st
from pathlib import Path


def setup_poetry_auth():
    """Set up Poetry authentication for private GCP repositories."""
    
    # Get service account credentials
    service_account_info = None
    
    # Try Streamlit secrets first
    try:
        if hasattr(st, 'secrets') and "gcp_service_account" in st.secrets:
            service_account_info = dict(st.secrets["gcp_service_account"])
    except:
        pass
    
    # Try environment variable
    if not service_account_info and "GCP_SERVICE_ACCOUNT" in os.environ:
        try:
            service_account_info = json.loads(os.environ["GCP_SERVICE_ACCOUNT"])
        except:
            pass
    
    if not service_account_info:
        return False
    
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
        token = credentials.token
        
        # Configure poetry with authentication
        repository_url = "https://europe-west4-python.pkg.dev/gpu-reservation-sarvam/sarvam-python-ci/simple/"
        
        # Set poetry authentication via environment variable
        os.environ["POETRY_HTTP_BASIC_SARVAM_PYTHON_CI_USERNAME"] = "oauth2accesstoken"
        os.environ["POETRY_HTTP_BASIC_SARVAM_PYTHON_CI_PASSWORD"] = token
        
        # Alternative: Configure poetry repository credentials
        subprocess.run([
            "poetry", "config", "http-basic.sarvam-python-ci", "oauth2accesstoken", token
        ], check=True, capture_output=True)
        
        print("✓ Poetry authentication configured successfully")
        return True
        
    except Exception as e:
        print(f"Error setting up poetry auth: {e}")
        return False
    
    finally:
        # Clean up temporary file
        if os.path.exists(credentials_file):
            os.unlink(credentials_file)


def install_dependencies():
    """Install dependencies using Poetry."""
    
    if not setup_poetry_auth():
        st.error("Failed to set up authentication for private packages")
        return False
    
    try:
        # Install dependencies using poetry
        result = subprocess.run([
            "poetry", "install", "--only", "main"
        ], capture_output=True, text=True, check=True)
        
        print("✓ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to install dependencies: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def ensure_dependencies():
    """Ensure all dependencies are installed."""
    
    # Check if private packages are available
    try:
        import sarvam_datatypes
        return True
    except ImportError:
        pass
    
    # Install dependencies if not available
    return install_dependencies()


if __name__ == "__main__":
    ensure_dependencies() 