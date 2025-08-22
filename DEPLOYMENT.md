# 🚀 Deployment Guide

This guide will walk you through deploying the Portfolio Optimizer to GitHub and Render.

## 📋 Prerequisites

- GitHub account
- Render account (free tier available)
- Git installed on your local machine

## 🔄 Step 1: GitHub Setup

### 1.1 Initialize Git Repository

```bash
# Navigate to your project directory
cd finance-analytics

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Portfolio Optimizer with modular architecture"

# Add your GitHub repository as remote
git remote add origin https://github.com/yourusername/finance-analytics.git

# Push to GitHub
git push -u origin main
```

### 1.2 Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right and select "New repository"
3. Name it `finance-analytics`
4. Make it **Public** (required for free Render deployment)
5. Don't initialize with README (we already have one)
6. Click "Create repository"

### 1.3 Push Your Code

```bash
# If you haven't already, push your code
git push -u origin main
```

## 🌐 Step 2: Render Deployment

### 2.1 Create Render Account

1. Go to [Render](https://render.com) and sign up
2. Connect your GitHub account
3. Choose the free plan

### 2.2 Deploy Using Blueprint (Recommended)

1. In Render dashboard, click "New +"
2. Select "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Click "Apply" to deploy

### 2.3 Manual Deployment (Alternative)

If you prefer manual setup:

1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `portfolio-optimizer`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r web_app/requirements.txt`
   - **Start Command**: `cd web_app && python app_production.py`
   - **Plan**: Free

### 2.4 Environment Variables

The application will work with default settings, but you can add environment variables in Render:

- `FLASK_ENV`: `production`
- `PYTHON_VERSION`: `3.9.16`

## 🔧 Step 3: Verify Deployment

### 3.1 Check Build Status

1. In Render dashboard, monitor the build process
2. Check build logs for any errors
3. Wait for deployment to complete

### 3.2 Test Your Application

1. Click on your service URL (e.g., `https://portfolio-optimizer.onrender.com`)
2. Test the health endpoint: `https://your-app.onrender.com/api/health`
3. Try the portfolio analysis features

### 3.3 Common Issues & Solutions

#### Build Failures
- **Missing dependencies**: Check `web_app/requirements.txt`
- **Python version**: Ensure compatibility with Python 3.9+
- **Import errors**: Verify all imports in `routes.py`

#### Runtime Errors
- **Port binding**: The production app uses `0.0.0.0` and `$PORT`
- **CORS issues**: CORS is enabled for all origins
- **Memory limits**: Free tier has 512MB RAM limit

## 🔄 Step 4: Continuous Deployment

### 4.1 Automatic Deployments

Once connected to GitHub, Render will automatically:
- Deploy when you push to the `main` branch
- Rebuild when you update dependencies
- Restart the service when needed

### 4.2 Manual Deployments

You can manually trigger deployments:
1. Go to your service in Render dashboard
2. Click "Manual Deploy"
3. Select the branch/commit to deploy

## 📊 Step 5: Monitoring & Maintenance

### 5.1 Monitor Performance

- **Logs**: Check application logs in Render dashboard
- **Metrics**: Monitor CPU, memory, and response times
- **Uptime**: Free tier may have cold starts

### 5.2 Update Your Application

```bash
# Make changes to your code
git add .
git commit -m "Update: Add new feature"
git push origin main

# Render will automatically deploy the changes
```

### 5.3 Scaling Considerations

**Free Tier Limitations:**
- 512MB RAM
- Shared CPU
- Cold starts (15-30 second initial load)
- 750 hours/month

**Upgrading to Paid:**
- More RAM and CPU
- Faster cold starts
- Custom domains
- SSL certificates

## 🔒 Step 6: Security & Best Practices

### 6.1 Environment Variables

Never commit sensitive data:
```bash
# Add to .gitignore
.env
.env.local
.env.production
```

### 6.2 API Keys

If you add external APIs later:
1. Store keys in Render environment variables
2. Access them in code: `os.environ.get('API_KEY')`

### 6.3 HTTPS

Render automatically provides:
- SSL certificates
- HTTPS redirects
- Secure headers

## 📈 Step 7: Analytics & Monitoring

### 7.1 Application Monitoring

Consider adding monitoring:
- **Logging**: Structured logging for debugging
- **Metrics**: Performance monitoring
- **Alerts**: Uptime monitoring

### 7.2 User Analytics

For user analytics, consider:
- Google Analytics
- Hotjar for user behavior
- Custom event tracking

## 🎯 Step 8: Custom Domain (Optional)

### 8.1 Add Custom Domain

1. In Render dashboard, go to your service
2. Click "Settings" → "Custom Domains"
3. Add your domain
4. Update DNS records as instructed

### 8.2 SSL Certificate

Render automatically provides SSL certificates for custom domains.

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [GitHub Pages](https://pages.github.com/) (for static documentation)

## 🆘 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements.txt` for missing packages
   - Verify Python version compatibility
   - Check build logs for specific errors

2. **App Won't Start**
   - Verify start command in `render.yaml`
   - Check if port binding is correct
   - Review application logs

3. **Import Errors**
   - Ensure all dependencies are in `requirements.txt`
   - Check import paths in `routes.py`
   - Verify file structure

4. **Cold Start Issues**
   - Free tier has 15-30 second cold starts
   - Consider upgrading to paid plan
   - Implement health checks

### Getting Help

- **Render Support**: [support@render.com](mailto:support@render.com)
- **GitHub Issues**: Create issues in your repository
- **Community**: Stack Overflow, Reddit r/webdev

---

**🎉 Congratulations!** Your Portfolio Optimizer is now live on the web!

**🔗 Your Live URL**: `https://your-app-name.onrender.com`
