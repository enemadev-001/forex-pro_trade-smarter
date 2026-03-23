# ForexPro - Professional Forex Trading Platform

## 🚀 Quick Start

### Requirements
- Python 3.7+
- Flask
- Flask-Login

### Installation
```bash
pip install -r requirements.txt
```

### Run Application
```bash
python app.py
```

### Access
- **Main Site**: http://127.0.0.1:5000/
- **Login**: http://127.0.0.1:5000/login
- **Admin Dashboard**: http://127.0.0.1:5000/dashboard

### Default Admin Account
- **Email**: admin@forexpro.com
- **Password**: admin123

## 📊 Features

### ✅ Core Features
- **Loading Page**: Professional animated landing
- **Live Forex Charts**: Real-time price monitoring
- **Position Calculator**: Accurate risk management
- **Academy**: Educational content with free lessons
- **User Authentication**: Secure login system
- **Admin Dashboard**: User management interface

### 🎯 Admin Capabilities
- View all registered users
- Delete user accounts
- Toggle admin privileges
- Real-time user registration tracking
- SQLite database storage

### 📁 Project Structure
```
forexpro-deployable/
├── app.py              # Main Flask application
├── models.py            # Database models and functions
├── requirements.txt       # Python dependencies
├── templates/           # HTML templates
│   ├── index.html       # Main landing page
│   ├── loading.html     # Loading animation
│   ├── login.html       # User login
│   ├── signup.html      # User registration
│   ├── dashboard.html   # Admin dashboard
│   └── academy.html     # Educational academy
└── static/              # CSS and JavaScript
    ├── style.css         # Main stylesheet
    └── script.js         # Interactive functionality
```

## 🔐 Security Notes

- Change default admin password before production
- Use environment variables for secret keys
- Enable HTTPS in production
- Consider adding email verification for production

## 🌐 Deployment

This folder is ready for deployment to any hosting service that supports Python Flask applications.

### Deployment Options:
- **Heroku**: Easy Flask deployment
- **PythonAnywhere**: Simple Python hosting
- **DigitalOcean**: Cloud server deployment
- **AWS**: Elastic Beanstalk or EC2

## 📞 Support

Built with ❤️ for Forex trading professionals
