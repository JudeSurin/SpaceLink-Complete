# SpaceLink Dashboard - Streamlit Cloud Deployment Guide

## Prerequisites

1. GitHub repository with your code
2. Streamlit Cloud account (free at https://streamlit.io/cloud)

## Deployment Steps

### 1. Ensure Requirements File Exists

The `requirements.txt` file is already created in the `spacelink-enterprise-gateway/` directory with all necessary dependencies:
- streamlit
- plotly
- pandas
- requests

### 2. Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Connect your GitHub repository
4. Configure the app:
   - **Repository**: Your GitHub repo (e.g., `yourusername/spacelink-complete`)
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `spacelink-enterprise-gateway/dashboard.py`
   - **Python version**: 3.9 or higher

### 3. Configure Secrets (Optional)

If your API Gateway is deployed separately, add secrets in Streamlit Cloud:

1. Go to your app settings
2. Click "Secrets"
3. Add the following:

```toml
API_BASE_URL = "https://your-api-gateway-url.com"
DEFAULT_USERNAME = "enterprise_admin"
DEFAULT_PASSWORD = "admin123"
```

### 4. Deploy

Click "Deploy" and wait for the app to build and launch.

## Troubleshooting

### Error: "No module named 'plotly'"

✅ **Fixed**: The `requirements.txt` file now includes plotly. Make sure it's in the `spacelink-enterprise-gateway/` directory.

### Error: "Cannot connect to API"

- If deploying only the dashboard (not the API Gateway), you need to:
  1. Deploy the API Gateway separately (e.g., on Heroku, Railway, or AWS)
  2. Update the `API_BASE_URL` secret in Streamlit Cloud to point to your deployed API

- If deploying both, you may need to:
  1. Deploy the API Gateway first
  2. Then deploy the dashboard with the correct API URL

### File Structure

Make sure your repository structure looks like this:

```
spacelink-complete/
├── spacelink-enterprise-gateway/
│   ├── dashboard.py          # Main dashboard file
│   ├── requirements.txt      # Dependencies (includes plotly!)
│   ├── .streamlit/
│   │   └── config.toml       # Streamlit configuration
│   └── ...
└── ...
```

## Notes

- The dashboard will work standalone, but it needs the API Gateway running to display data
- For local development, the API Gateway should run on `http://127.0.0.1:8000`
- For cloud deployment, update the `API_BASE_URL` to point to your deployed API Gateway

