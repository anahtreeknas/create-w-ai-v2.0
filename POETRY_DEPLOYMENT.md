# Poetry-based Deployment Guide for Streamlit Cloud

This guide explains how to deploy your Poetry-managed app to Streamlit Cloud with private GCP packages.

## How it Works

1. **Poetry Configuration**: Your `pyproject.toml` already has the private GCP source configured
2. **Requirements Generation**: We generated `requirements.txt` from Poetry, excluding private packages
3. **Runtime Installation**: Private packages are installed at runtime using GCP authentication

## Files Created

- `requirements.txt` - Public dependencies (generated from Poetry)
- `auth_setup.py` - Handles GCP authentication and private package installation
- `poetry_auth.py` - Alternative Poetry-specific authentication (optional)

## Setup Steps

### 1. Configure GCP Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a service account with `Artifact Registry Reader` role
3. Download the JSON key file

### 2. Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Deploy to [share.streamlit.io](https://share.streamlit.io/)
3. In app settings, add secrets:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

### 3. Update Your App

Add this to the beginning of your `streamlit_app.py`:

```python
# Import authentication handler
from auth_setup import ensure_authentication

# Ensure private packages are available
if not ensure_authentication():
    st.error("Failed to authenticate with GCP. Please check your credentials.")
    st.stop()
```

## Local Development

For local development, you can use Poetry normally:

```bash
# Install dependencies locally
poetry install

# Run the app
poetry run streamlit run streamlit_app.py
```

## Alternative: Using Poetry Export

If you prefer to use Poetry's export feature regularly:

```bash
# Export without private packages
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Then remove private packages manually or use grep:
grep -v "sarvam-" requirements.txt > requirements_public.txt
mv requirements_public.txt requirements.txt
```

## Key Benefits

1. **Poetry Workflow**: Keep using Poetry for dependency management
2. **Clean Separation**: Public packages in requirements.txt, private packages handled separately
3. **Secure**: Credentials stored in Streamlit secrets, not in code
4. **Flexible**: Easy to update private packages by modifying `auth_setup.py`

## Troubleshooting

### Authentication Issues
- Check that your service account has correct permissions
- Verify the service account JSON is properly formatted in secrets
- Ensure the service account can access the specific packages

### Package Installation Issues
- Check package versions in `auth_setup.py`
- Verify the registry URL is correct
- Look at Streamlit Cloud logs for detailed error messages

### Import Errors
- Make sure `auth_setup.py` is imported before your modules that use private packages
- Check that private packages are being installed successfully

## Updating Dependencies

To update dependencies:

1. **Update Poetry**: `poetry update`
2. **Export new requirements**: `poetry export -f requirements.txt --output requirements_temp.txt --without-hashes`
3. **Remove private packages**: Edit out the private packages
4. **Update auth_setup.py**: Update version numbers if needed
5. **Commit and redeploy**

---

This approach gives you the best of both worlds: Poetry's excellent dependency management locally, and compatibility with Streamlit Cloud's deployment requirements. 