# Debugging Vercel Deployment Errors

**Your Errors**:
```
503 - /api/auth/login (Service Unavailable)
401 - /api/auth/verify (Unauthorized)
```

---

## 🔍 What These Errors Mean

### 503 Service Unavailable
**Meaning**: Your frontend **cannot reach** the backend at all.

**Causes**:
1. ❌ `NEXT_PUBLIC_API_URL` environment variable is **NOT SET** in Vercel
2. ❌ Frontend is trying to call `http://localhost:8000` (which doesn't exist in production)
3. ❌ Backend is down/not deployed on Railway
4. ❌ Wrong backend URL configured

### 401 Unauthorized
**Meaning**: Authentication token is missing or invalid.

**Why**: This happens **after** the 503 - when frontend can't login, it has no valid token.

---

## ✅ Quick Diagnosis

### Step 1: Check Browser Network Tab

1. **Open your Vercel site**: https://q4-hackathon2-todo-fullstack.vercel.app
2. **Press F12** (Developer Tools)
3. **Go to Network tab**
4. **Try to login**
5. **Click on the failed `/api/auth/login` request**
6. **Look at "General" → "Request URL"**

**What do you see?**

#### ❌ If you see: `http://localhost:8000/auth/login`
**Problem**: Environment variable NOT set in Vercel
**Fix**: See Step 2 below

#### ❌ If you see: `https://something.railway.app/auth/login` (and it fails)
**Problem**: Backend is down or CORS issue
**Fix**: See Step 3 below

---

## 🛠️ Step 2: Set Vercel Environment Variable

**This is the #1 most common issue!**

### A. Find Your Railway Backend URL

**Test if your backend is running**:

```bash
# Replace with YOUR actual Railway URL
curl https://YOUR-BACKEND.railway.app/health

# Expected response:
{"status":"healthy"}

# If this fails, your backend is NOT running!
```

**Don't know your Railway URL?**
1. Go to: https://railway.app/
2. Open your backend project
3. Look for the deployment URL (e.g., `https://web-production-XXXX.railway.app`)

### B. Set Environment Variable in Vercel

1. **Go to Vercel Dashboard**:
   https://vercel.com/your-username/q4-hackathon2-todo-fullstack/settings/environment-variables

2. **Click "Add New"**

3. **Enter**:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://YOUR-BACKEND.railway.app` ← **PASTE YOUR ACTUAL RAILWAY URL**
   - **Environments**: Check ALL boxes (Production, Preview, Development)

4. **Click "Save"**

### C. Redeploy Vercel

**CRITICAL**: Environment variables only work in NEW deployments!

1. Go to: https://vercel.com/your-username/q4-hackathon2-todo-fullstack/deployments
2. Click "..." menu on latest deployment
3. Click "Redeploy"
4. Wait 1-2 minutes

### D. Verify It Worked

1. **Wait for deployment to finish**
2. **Refresh your browser** (Ctrl + Shift + R)
3. **Open DevTools** (F12) → Network tab
4. **Try to login again**
5. **Check Request URL** - should now be `https://YOUR-BACKEND.railway.app/auth/login`

---

## 🛠️ Step 3: Fix Backend Issues

If you see requests going to Railway but getting 503/500 errors:

### A. Check Railway Backend is Running

```bash
# Test health endpoint
curl https://YOUR-BACKEND.railway.app/health

# Expected: {"status":"healthy"}
```

**If this fails**:
1. Go to Railway dashboard
2. Check deployment logs
3. Look for errors
4. Make sure backend is deployed and running

### B. Check CORS Configuration

Your backend MUST allow requests from Vercel:

1. **Go to Railway**: https://railway.app/ → Backend service → Variables

2. **Find `CORS_ORIGINS` variable**

3. **Should be**:
   ```
   http://localhost:3000,https://q4-hackathon2-todo-fullstack.vercel.app,https://q4-hackathon2-todo-fullstack-*.vercel.app
   ```

4. **If missing or wrong**: Update it and save (Railway will auto-redeploy)

### C. Test CORS with curl

```bash
# Test CORS from your Vercel domain
curl -H "Origin: https://q4-hackathon2-todo-fullstack.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://YOUR-BACKEND.railway.app/auth/login -v

# Look for "Access-Control-Allow-Origin" in response headers
# Should include your Vercel domain
```

---

## 🔍 Advanced Debugging

### Check Vercel Build Logs

1. Go to: https://vercel.com/your-username/q4-hackathon2-todo-fullstack/deployments
2. Click latest deployment
3. Click "Build Logs"
4. Search for: `NEXT_PUBLIC_API_URL`

**Expected**:
```
NEXT_PUBLIC_API_URL: https://YOUR-BACKEND.railway.app
```

**If you see**:
```
NEXT_PUBLIC_API_URL: undefined
```
→ Environment variable is NOT set!

### Check Runtime Logs

1. Vercel → Deployments → Latest → Functions
2. Click "View Function Logs"
3. Look for errors related to backend calls

### Check Railway Logs

1. Railway → Backend service → Deployments
2. Click latest deployment
3. Click "View Logs"
4. Look for incoming requests from Vercel
5. Check for CORS errors

---

## 📋 Complete Troubleshooting Checklist

Work through this in order:

### Vercel Frontend
- [ ] Environment variable `NEXT_PUBLIC_API_URL` is set in Vercel
- [ ] Value is your Railway backend URL (e.g., `https://web-production-XXXX.railway.app`)
- [ ] Variable is enabled for Production, Preview, Development
- [ ] You've redeployed after setting the variable
- [ ] Build logs show: `NEXT_PUBLIC_API_URL: https://...railway.app`
- [ ] Browser Network tab shows requests going to Railway (not localhost)

### Railway Backend
- [ ] Backend is deployed and running on Railway
- [ ] Health endpoint returns: `curl https://YOUR-BACKEND.railway.app/health` → `{"status":"healthy"}`
- [ ] Environment variable `CORS_ORIGINS` includes your Vercel domain
- [ ] CORS value: `http://localhost:3000,https://q4-hackathon2-todo-fullstack.vercel.app,https://q4-hackathon2-todo-fullstack-*.vercel.app`
- [ ] Backend logs show incoming requests from Vercel
- [ ] No CORS errors in Railway logs

### Browser
- [ ] Hard refresh (Ctrl + Shift + R) to clear cache
- [ ] DevTools → Network → Disable cache checkbox is checked
- [ ] No browser extensions blocking requests
- [ ] Console shows no CORS errors
- [ ] Network tab shows correct Request URL (Railway, not localhost)

---

## 🎯 Most Common Solutions

### Problem: 503 on login
**Solution**: Set `NEXT_PUBLIC_API_URL` in Vercel and redeploy

### Problem: CORS errors
**Solution**: Add Vercel domain to `CORS_ORIGINS` in Railway

### Problem: Still getting localhost
**Solution**: Clear Vercel build cache and redeploy

### Problem: Backend unreachable
**Solution**: Check Railway backend is running and deployed

---

## 💡 Quick Verification Commands

Run these to verify everything:

```bash
# 1. Test Railway backend health
curl https://YOUR-BACKEND.railway.app/health
# Expected: {"status":"healthy"}

# 2. Test Railway backend from Vercel domain
curl -H "Origin: https://q4-hackathon2-todo-fullstack.vercel.app" \
     https://YOUR-BACKEND.railway.app/health
# Should return same response with CORS headers

# 3. Check Vercel environment variables
vercel env ls
# Should show: NEXT_PUBLIC_API_URL (Production, Preview, Development)

# 4. Test full login flow
curl -X POST https://YOUR-BACKEND.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"TestPass123"}'
# Should return tokens
```

---

## 📊 Expected vs Current State

### ❌ Current (Broken)
```
Browser (Vercel): https://q4-hackathon2-todo-fullstack.vercel.app
   ↓ tries to call
Backend: http://localhost:8000  ← DOESN'T EXIST!
   ↓
Error: 503 Service Unavailable
```

### ✅ After Fix
```
Browser (Vercel): https://q4-hackathon2-todo-fullstack.vercel.app
   ↓ calls (via NEXT_PUBLIC_API_URL)
Backend (Railway): https://YOUR-BACKEND.railway.app
   ↓ allows request (via CORS_ORIGINS)
Success: 200 OK with tokens
```

---

## 🆘 Still Not Working?

If you've tried everything above, provide these details:

1. **Your Railway backend URL**: `https://...`
2. **Screenshot of Vercel environment variables** (Settings → Environment Variables)
3. **Screenshot of Railway environment variables** (Service → Variables)
4. **Browser console output** (F12 → Console tab - copy all errors)
5. **Network tab screenshot** showing the failed request URL
6. **Vercel build logs** showing NEXT_PUBLIC_API_URL value
7. **Railway deployment logs** showing any errors

---

## 🎯 The Fix (99% of Cases)

**In Vercel**:
1. Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL` = `https://YOUR-BACKEND.railway.app`
3. Deployments → Redeploy

**In Railway**:
1. Backend service → Variables
2. Add/Update: `CORS_ORIGINS` = `http://localhost:3000,https://q4-hackathon2-todo-fullstack.vercel.app`
3. Save (auto-redeploys)

**Wait 2-3 minutes**, then test again!
