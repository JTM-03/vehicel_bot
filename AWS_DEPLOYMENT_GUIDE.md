# 🚀 Vehicle Bot - Local Setup & AWS Deployment Guide

## Part 1: Run Locally in VS Code

### Step 1: Start the Streamlit Server

```bash
cd d:\Vehicle_Bot
streamlit run app.py
```

You'll see:
```
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### Step 2: Open in Browser

Click the link or go to **http://localhost:8501** in your browser.

### Step 3: Test the App

1. **Add a new vehicle**:
   - Enter: Wagon R, Maharagama, Colombo
   - Add 3 trips with dates
   - Click "💾 Save User Profile to Database"

2. **Load the user**:
   - Use "📂 Load Existing User" dropdown
   - Click "⬇️ Load Selected User"
   - Form auto-fills ✅

3. **View changes**:
   - Go to "📝 Changes Log" tab
   - See all modifications tracked

### Environment Variables (.env)

The app needs:
```
GROQ_API_KEY=your_api_key_here
MONGO_URI=your_mongodb_connection_string (optional)
```

✅ Already configured in `.env` file

---

## Part 2: Deploy to AWS

### Option A: Streamlit Cloud (Easiest) ⭐ RECOMMENDED

**Pros**: 
- Free tier available
- Auto-deploys from GitHub
- No server management
- Built for Streamlit

**Steps**:

1. **Push code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial Vehicle Bot v1.1.0"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/vehicle-bot.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Select your repository
   - Branch: `main`
   - File path: `app.py`
   - Click "Deploy"

3. **Add Secrets**:
   - In Streamlit Cloud dashboard
   - Settings → Secrets
   - Add your environment variables:
     ```
     GROQ_API_KEY = "your_key_here"
     MONGO_URI = "your_mongodb_uri"
     ```

4. **Done!** 🎉
   - Your app is live at: `https://your-app-name.streamlit.app`

---

### Option B: AWS EC2 (Full Control)

**Pros**: 
- Complete control
- Custom domain
- Scalable
- Can run other services

**Steps**:

#### 1. Create EC2 Instance

```bash
# On AWS Console:
# - Launch Instance
# - Ubuntu 22.04 LTS
# - t3.micro (free tier)
# - Security group: Allow HTTP (80), HTTPS (443), SSH (22)
```

#### 2. SSH into Server

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 3. Install Dependencies

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip git -y

# Install system libraries
sudo apt install libssl-dev libffi-dev python3-dev -y
```

#### 4. Clone Your Code

```bash
git clone https://github.com/YOUR_USERNAME/vehicle-bot.git
cd vehicle-bot
```

#### 5. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 6. Configure Environment

```bash
# Create .env file
nano .env
```

Add your secrets:
```
GROQ_API_KEY=your_key
MONGO_URI=your_mongodb_uri
```

Press `Ctrl+X`, then `Y`, then Enter to save.

#### 7. Run with PM2 (Background Process)

```bash
# Install Node.js and PM2
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
sudo npm install -g pm2

# Create PM2 config file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'vehicle-bot',
    script: 'streamlit',
    args: 'run app.py --server.port 8501 --server.address 0.0.0.0',
    instances: 1,
    autorestart: true,
    watch: false,
    env: {
      NODE_ENV: 'production'
    }
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

#### 8. Setup Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install nginx -y

# Create config
sudo tee /etc/nginx/sites-available/vehicle-bot > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/vehicle-bot /etc/nginx/sites-enabled/

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. Add SSL Certificate (Free with Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

#### 10. Access Your App

Visit: `https://your-domain.com` ✅

---

### Option C: AWS Lambda + API Gateway (Serverless)

**Pros**:
- Pay only for usage
- Auto-scales
- No server management

**Challenge**: Streamlit isn't designed for Lambda (stateless). Better to use Option A or B.

---

### Option D: Docker + AWS ECS

**Pros**:
- Containerized
- Easy deployment
- Consistent environments

**Steps**:

1. **Create Dockerfile** in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Create .dockerignore**:

```
.venv
.git
.env
__pycache__
.pytest_cache
```

3. **Build locally** (test):

```bash
docker build -t vehicle-bot .
docker run -p 8501:8501 --env-file .env vehicle-bot
```

4. **Push to AWS ECR**:

```bash
# Create ECR repository
aws ecr create-repository --repository-name vehicle-bot

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag vehicle-bot:latest your-account.dkr.ecr.us-east-1.amazonaws.com/vehicle-bot:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/vehicle-bot:latest
```

5. **Deploy on ECS**:
   - Create ECS cluster
   - Create task definition (point to ECR image)
   - Create service (auto-scales)
   - Attach load balancer

---

## Comparison Table

| Method | Setup Time | Cost | Maintenance | Best For |
|--------|-----------|------|-------------|----------|
| **Streamlit Cloud** | 5 min | Free/paid | None | Quick deploy, testing |
| **EC2 + Nginx** | 30 min | $5-20/month | Medium | Production, custom domain |
| **Docker + ECS** | 45 min | $15-50/month | Low | Scaling, teams |
| **Lambda** | Not recommended | Variable | Medium | Not suitable for Streamlit |

---

## Recommended: Streamlit Cloud + Custom Domain

### Setup (5 minutes):

1. **Deploy to Streamlit Cloud** (steps above)
2. **Buy domain** (Namecheap, GoDaddy)
3. **In Streamlit Cloud Settings**:
   - Go to Advanced settings
   - Custom domain: `yourdomain.com`
   - Add CNAME record to your registrar pointing to Streamlit

### Result:
- Your app at `https://yourdomain.com`
- Auto-HTTPS
- Free SSL
- Auto-scaling
- 0 server management

---

## Database Setup for Production

### MongoDB Atlas (Recommended)

1. **Create free cluster** at https://www.mongodb.com/cloud/atlas
2. **Get connection string**
3. **Add to Streamlit Cloud Secrets**:
   ```
   MONGO_URI = mongodb+srv://user:pass@cluster.mongodb.net/vehicle_bot_db?retryWrites=true&w=majority
   ```

### Data Backup

```bash
# Backup MongoDB (local)
mongodump --uri "mongodb+srv://user:pass@cluster.mongodb.net/vehicle_bot_db" --out ./backup

# Restore
mongorestore --uri "mongodb+srv://user:pass@cluster.mongodb.net/vehicle_bot_db" ./backup
```

---

## Monitoring & Logs

### Streamlit Cloud
- Logs visible in dashboard
- Auto-restarts on crashes

### EC2
```bash
# View Streamlit logs
pm2 logs vehicle-bot

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### CloudWatch (AWS)
```bash
# Enable CloudWatch for logs
sudo apt install awslogs -y
```

---

## Security Checklist

- ✅ Keep `.env` files secret (never commit)
- ✅ Use environment variables, not hardcoded secrets
- ✅ Enable HTTPS (free with Let's Encrypt)
- ✅ Restrict MongoDB access (IP whitelisting)
- ✅ Keep dependencies updated
- ✅ Regular backups of MongoDB
- ✅ Use SSH keys for EC2 (never passwords)

---

## Quick Command Reference

```bash
# Local development
streamlit run app.py

# Check if running
curl http://localhost:8501

# Kill Streamlit
pkill -f "streamlit run"

# AWS EC2 - SSH
ssh -i key.pem ubuntu@instance-ip

# AWS EC2 - Copy files
scp -i key.pem -r ./vehicle-bot ubuntu@instance-ip:~/

# PM2 management
pm2 start ecosystem.config.js
pm2 stop vehicle-bot
pm2 restart vehicle-bot
pm2 logs vehicle-bot
pm2 delete vehicle-bot
```

---

## Troubleshooting

### App crashes on deploy
```bash
# Check logs
streamlit run app.py  # Run locally first

# Check for syntax errors
python -m py_compile app.py database.py logic.py
```

### Slow MongoDB queries
```javascript
// Create indexes in MongoDB Atlas
db.users.createIndex({ "model": 1, "city": 1 });
db.users.createIndex({ "created_date": -1 });
```

### Memory issues on EC2
```bash
# Check memory usage
free -h

# Upgrade instance type (stop first, then change)
# t3.micro → t3.small → t3.medium
```

---

## Summary

1. **Test locally**: `streamlit run app.py` ✅
2. **Deploy to Streamlit Cloud**: 5 min ⭐ RECOMMENDED
3. **Optional**: Add custom domain
4. **Optional**: Scale to EC2/Docker if needed

**Your app is now LIVE!** 🎉

---

**Need Help?**
- Streamlit docs: https://docs.streamlit.io
- AWS docs: https://docs.aws.amazon.com
- MongoDB docs: https://docs.mongodb.com
