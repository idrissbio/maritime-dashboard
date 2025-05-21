# Streamlit Cloud Deployment Guide

This guide walks through the steps to deploy the Maritime Trading Dashboard to Streamlit Cloud.

## Prerequisites

- GitHub account
- Repository with your code (public or private)
- Streamlit Cloud account (connected to your GitHub)

## Deployment Steps

1. **Ensure your repository includes these files:**
   - `deploy-streamlit.py` - Self-contained Streamlit application
   - `requirements.txt` - Compatible package versions
   - `.streamlit/config.toml` - Streamlit configuration

2. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push
   ```

3. **Deploy to Streamlit Cloud:**
   - Go to [Streamlit Cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository
   - Configure deployment settings:
     * Main file path: `deploy-streamlit.py`
     * Branch: `main` (or your preferred branch)
     * Advanced settings: No additional Python packages or requirements needed
   - Click "Deploy"

4. **Wait for deployment:**
   - Streamlit Cloud will install dependencies and start your app
   - This process usually takes 1-3 minutes
   - If there are any errors, they will be displayed in the log

5. **Access your deployed app:**
   - Once deployment is complete, you'll get a URL for your app
   - The URL format is typically: `https://username-repo-name.streamlit.app`

## Troubleshooting

If you encounter deployment issues:

### Dependencies Issues
- Make sure your `requirements.txt` uses compatible versions
- The versions in this project have been tested with Streamlit Cloud
- Avoid using the latest packages as they might not be compatible

### Resource Limits
- Streamlit Cloud has memory limits (1GB by default)
- If your app exceeds these limits, try optimizing your code
- Reduce data size or use caching for computationally expensive operations

### API Access Issues
- Check if TwelveData API is accessible from Streamlit Cloud
- Ensure your API requests have proper error handling
- The app includes fallback mechanisms for API failures

## Maintenance

To update your deployed app:

1. Make changes to your code locally
2. Push changes to GitHub
3. Streamlit Cloud will automatically redeploy your app

## Alternative Deployment Options

If Streamlit Cloud doesn't meet your needs, consider:

- Heroku (using the included Procfile)
- AWS Elastic Beanstalk
- Google Cloud Run
- Docker container deployment