# Vercel Deployment Configuration Guide

**Frontend URL**: https://q4-hackathon2-todo-fullstack.vercel.app/

## 🚨 Current Issue: "Authentication service unavailable"

### Root Cause

Your Vercel frontend is trying to connect to `http://localhost:8000` (development backend), but needs to connect to your **Railway production backend**.

### Why This Happens

1. **Vercel** deployed your frontend to production
2. Frontend code reads `NEXT_PUBLIC_API_URL` from environment variables
3. Environment variable is **NOT SET** in Vercel (defaults to localhost)
4. Frontend tries to call `http://localhost:8000/auth/login` → **FAILS**
5. Error: "Authentication service unavailable"

---

## ✅ Solution: Configure Vercel Environment Variables

### Step 1: Get Your Railway Backend URL

**Option A: Find in Railway Dashboard**
1. Go to: https://railway.app/
2. Open your project
3. Find your backend service
4. Copy the **Public URL** (e.g., `https://q4-hackathon2-todo-backend.railway.app`)

**Option B: Check Railway Deployment Logs**
1. Railway dashboard → Your service → Deployments
2. Look for: "Deployed to https://..."
3. Copy that URL

**Option C: Test if Backend is Running**
```bash
# Replace with your actual Railway URL
curl https://your-backend.railway.app/health

# Expected response:
{"status":"healthy"}
```

---

### Step 2: Set Environment Variable in Vercel

**Method 1: Via Vercel Dashboard (Recommended)**

1. **Go to your Vercel project**:
   https://vercel.com/your-username/q4-hackathon2-todo-fullstack

2. **Click**: Settings → Environment Variables

3. **Add New Variable**:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-railway-backend.railway.app` (your actual Railway URL)
   - **Environments**:
     - ✓ Production
     - ✓ Preview
     - ✓ Development

4. **Save** the variable

**Method 2: Via Vercel CLI**

```bash
# Install Vercel CLI if needed
npm i -g vercel

# Login
vercel login

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL production
# When prompted, paste your Railway URL: https://your-railway-backend.railway.app

# Also set for preview and development
vercel env add NEXT_PUBLIC_API_URL preview
vercel env add NEXT_PUBLIC_API_URL development
```

---

### Step 3: Redeploy to Apply Changes

**IMPORTANT**: Environment variables only apply to **NEW** deployments!

**Option A: Redeploy from Vercel Dashboard**
1. Go to: Deployments tab
2. Find the latest deployment
3. Click the **"..."** menu button
4. Click **"Redeploy"**
5. Check "Use existing Build Cache" (optional, faster)
6. Click **"Redeploy"**

**Option B: Trigger Redeploy via Git Push**
```bash
# Make a small change (e.g., add a space to README)
git commit --allow-empty -m "trigger Vercel redeploy with updated env vars"
git push origin main
```

**Option C: Redeploy via Vercel CLI**
```bash
vercel --prod
```

---

### Step 4: Verify the Fix

1. **Wait for deployment** (1-2 minutes)

2. **Visit your frontend**:
   https://q4-hackathon2-todo-fullstack.vercel.app

3. **Open Browser DevTools**:
   - Press F12
   - Go to **Network** tab
   - Try to login/register

4. **Check Network Requests**:
   - Look for requests to `/api/auth/login`
   - Click on the request
   - Check "Headers" → "Request URL"
   - Should show: `https://your-railway-backend.railway.app/auth/login` ✅
   - NOT: `http://localhost:8000/auth/login` ❌

5. **Expected Result**:
   - ✅ Login/Register works
   - ✅ No "Authentication service unavailable" error
   - ✅ You can create/view/edit todos

---

## 🔍 Troubleshooting

### Still Getting "Authentication service unavailable"?

**Check 1: Environment Variable Set Correctly**
```bash
# View all Vercel env vars
vercel env ls

# Should show:
# NEXT_PUBLIC_API_URL (Production, Preview, Development)
```

**Check 2: Railway Backend is Running**
```bash
# Test backend health endpoint
curl https://your-railway-backend.railway.app/health

# Expected: {"status":"healthy"}
# If fails: Backend is down or URL is wrong
```

**Check 3: CORS Configuration**

Backend must allow requests from your Vercel domain:

```python
# In backend/app/main.py
origins = [
    "http://localhost:3000",
    "https://q4-hackathon2-todo-fullstack.vercel.app",  # ← Add this!
    # Add any other Vercel preview URLs if needed
]
```

Update CORS in Railway:
1. Railway → Your backend service → Variables
2. Add/Update: `CORS_ORIGINS`
3. Value: `http://localhost:3000,https://q4-hackathon2-todo-fullstack.vercel.app`
4. Redeploy backend

**Check 4: Vercel Build Logs**
1. Vercel → Deployments → Latest deployment
2. Click "View Build Logs"
3. Search for: `NEXT_PUBLIC_API_URL`
4. Should see: `NEXT_PUBLIC_API_URL: https://your-railway-backend.railway.app`

**Check 5: Clear Vercel Build Cache**
1. Vercel → Settings → General
2. Scroll to "Build & Development Settings"
3. Click "Clear Build Cache"
4. Redeploy

---

## 📊 Quick Verification Checklist

Before proceeding, verify:

- [ ] Railway backend is deployed and running
- [ ] Railway backend health endpoint returns `{"status":"healthy"}`
- [ ] Vercel environment variable `NEXT_PUBLIC_API_URL` is set
- [ ] Environment variable value is your Railway URL (not localhost)
- [ ] Environment variable is enabled for Production, Preview, Development
- [ ] You've redeployed after setting the variable
- [ ] Backend CORS allows your Vercel domain
- [ ] Frontend builds successfully in Vercel
- [ ] Network requests in browser go to Railway URL (not localhost)

---

## 🎯 Expected vs Actual

### ❌ Current (Broken)
```
Frontend: https://q4-hackathon2-todo-fullstack.vercel.app
   ↓ tries to call
Backend:  http://localhost:8000  ← DOESN'T EXIST in production!
   ↓
Result:   "Authentication service unavailable"
```

### ✅ After Fix
```
Frontend: https://q4-hackathon2-todo-fullstack.vercel.app
   ↓ calls
Backend:  https://your-railway-backend.railway.app  ← CORRECT!
   ↓
Result:   Authentication works! 🎉
```

---

## 🔗 Helpful Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Vercel Environment Variables Docs**: https://vercel.com/docs/concepts/projects/environment-variables
- **Railway Dashboard**: https://railway.app/
- **Your Frontend**: https://q4-hackathon2-todo-fullstack.vercel.app/
- **Your Backend**: https://your-railway-backend.railway.app (replace with actual URL)

---

## 📝 Summary

**Problem**: Frontend can't find backend
**Cause**: Environment variable not set in Vercel
**Fix**: Set `NEXT_PUBLIC_API_URL` to Railway backend URL
**Time**: ~5 minutes to configure

**Once fixed**: Full-stack app will work in production! 🚀
