# Railway Deployment Setup Guide

## Prerequisites
- Railway account
- GitHub repository connected to Railway
- PostgreSQL database (can be created in Railway)

## Step 1: Create PostgreSQL Database in Railway

1. Go to your Railway project dashboard
2. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a Postgres database and provide connection details
4. **Important**: Railway automatically sets the `DATABASE_URL` environment variable

## Step 2: Configure Environment Variables

Go to your Railway service → **Variables** tab and add the following:

### Required Variables:

```bash
# Database (if not using Railway Postgres, set this manually)
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require

# JWT Configuration
SECRET_KEY=<generate-a-secure-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Configuration
DEBUG=false
CORS_ORIGINS=https://your-frontend-url.vercel.app

# Optional: Rate Limiting
LOGIN_RATE_LIMIT=5
```

### How to Generate SECRET_KEY:

Run this in your terminal:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Or use this one (for development only):
```
7e9c6587d261ae0045fe2d1edf5d6c4092fbf2a78861bba727def768504b53dd
```

## Step 3: Update CORS_ORIGINS

Once your Vercel frontend is deployed, update the `CORS_ORIGINS` variable:

```bash
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

You can add multiple origins separated by commas.

## Step 4: Deploy

1. Railway auto-deploys on push to GitHub
2. Check the **Deploy Logs** for any errors
3. Once deployed, Railway provides a public URL like: `https://your-app.railway.app`

## Step 5: Verify Deployment

Test the health endpoint:
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{"status": "healthy"}
```

## Common Issues

### Issue: "Could not parse SQLAlchemy URL"
**Solution**: Ensure `DATABASE_URL` is set in Railway variables. If using Railway Postgres, it should be automatically set.

### Issue: Database connection timeout
**Solution**: Ensure your Railway Postgres database is in the same region as your backend service.

### Issue: CORS errors from frontend
**Solution**: Update `CORS_ORIGINS` to include your Vercel frontend URL.

## Project Structure

- **Root Directory**: Set to `phase2-fullstack/backend` in Railway settings
- **Build Command**: Auto-detected (pip install)
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| SECRET_KEY | Yes | - | JWT signing key (must be secure) |
| ALGORITHM | No | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | No | 30 | Access token lifetime |
| REFRESH_TOKEN_EXPIRE_DAYS | No | 7 | Refresh token lifetime |
| CORS_ORIGINS | No | http://localhost:3000 | Comma-separated allowed origins |
| DEBUG | No | false | Enable debug mode |
| LOGIN_RATE_LIMIT | No | 5 | Login attempts per window |
