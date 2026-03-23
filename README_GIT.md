# 🚀 Git Setup for Vercel Deployment

## 📋 Prerequisites
1. **Install Git**: https://git-scm.com/download/win
2. **Create GitHub account**: https://github.com/signup
3. **Create Vercel account**: https://vercel.com/signup

## 🔄 Step-by-Step Git Setup

### 1. Install Git (if not installed)
```bash
# Download from: https://git-scm.com/download/win
# Run installer with default options
```

### 2. Open Command Prompt/PowerShell
```bash
# Navigate to your project folder
cd c:\Users\USER\Desktop\forexpro-html\forexpro-deployable
```

### 3. Configure Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 4. Initialize Git Repository
```bash
git init
```

### 5. Add All Files
```bash
git add .
```

### 6. Make First Commit
```bash
git commit -m "Initial ForexPro deployment with public access"
```

### 7. Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `forexpro`
3. Make it Public
4. Click "Create repository"

### 8. Connect to GitHub
```bash
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/forexpro.git

# Push to GitHub
git push -u origin main
```

## 🌐 Vercel Deployment

### Option 1: Connect GitHub to Vercel (Recommended)
1. **Login to Vercel**: https://vercel.com/login
2. **Click "New Project"**
3. **"Import Git Repository"**
4. **Select your forexpro repo**
5. **Framework Preset**: "Python"
6. **Root Directory**: `.` (default)
7. **Build Command**: `pip install -r requirements.txt`
8. **Start Command**: `gunicorn app:app`
9. **Click "Deploy"**

### Option 2: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project folder
cd c:\Users\USER\Desktop\forexpro-html\forexpro-deployable
vercel --prod
```

## 📁 Files Ready for Deployment

Your `forexpro-deployable` folder contains:
- ✅ `app.py` - Main Flask application
- ✅ `models.py` - Database functions  
- ✅ `requirements.txt` - Python dependencies
- ✅ `vercel.json` - Vercel configuration
- ✅ `.gitignore` - Files to exclude
- ✅ `templates/` - HTML templates
- ✅ `static/` - CSS and JavaScript
- ✅ `README.md` - Documentation

## 🔧 Vercel Configuration Details

The `vercel.json` file handles:
- **Python runtime** version 3.9
- **Build process** installs dependencies
- **Routing** all requests to `app.py`
- **Serverless** deployment

## 🚨 Important Notes

### Database on Vercel:
- Vercel uses **serverless functions**
- Database will be **read-only** in serverless
- For production, consider:
  - **Vercel KV** for simple data
  - **External database** (Supabase, PlanetScale)
  - **Firebase** for user data

### Environment Variables:
Set these in Vercel dashboard:
- `SECRET_KEY` (generate random string)
- `DATABASE_URL` (if using external DB)

## 🎯 After Deployment

1. **Vercel provides URL**: `https://forexpro-xyz.vercel.app`
2. **Test all features**: signup, login, dashboard
3. **Custom domain**: Add in Vercel settings if needed

## 🔄 Update Workflow

When you make changes:
```bash
# Add changes
git add .

# Commit changes
git commit -m "Update feature description"

# Push to GitHub
git push origin main

# Vercel auto-deploys!
```

## 🆘 Troubleshooting

### "Build Failed":
- Check `requirements.txt` syntax
- Verify Python version in `vercel.json`
- Check for missing files

### "404 Errors":
- Verify `vercel.json` routing
- Check file paths in `app.py`

### "Database Issues":
- Vercel serverless has limitations
- Consider external database for production

---

**🎯 Your ForexPro is ready for global deployment on Vercel!**
