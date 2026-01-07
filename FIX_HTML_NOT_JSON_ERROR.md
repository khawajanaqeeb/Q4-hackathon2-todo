# Fix: "Unexpected token '<', "<!DOCTYPE "... is not valid JSON"

**Error Type**: Frontend trying to parse HTML as JSON
**Common Cause**: Backend returning error page instead of JSON

---

## 🔍 What This Error Means

Your frontend code does this:
```javascript
const response = await fetch('/api/auth/login');
const data = await response.json(); // ← Expects JSON
```

But the backend returns this:
```html
<!DOCTYPE html>
<html>
  <head><title>404 Not Found</title></head>
  <body>Page not found</body>
</html>
```

JavaScript tries to parse HTML as JSON → **ERROR!**

---

## 🚨 Most Common Causes

### 1. ❌ Backend URL is Wrong or Not Set

**Problem**: `NEXT_PUBLIC_API_URL` points to wrong URL or not set at all

**Check**:
```javascript
// In browser console on https://q4-hackathon2-todo-fullstack.vercel.app
console.log(process.env.NEXT_PUBLIC_API_URL);

// Should show: "https://your-backend.railway.app"
// If shows: undefined or localhost → WRONG!
```

**Fix**: Set correct Railway URL in Vercel environment variables

### 2. ❌ Backend Route Doesn't Exist

**Problem**: Frontend calls `/auth/login` but backend expects `/api/auth/login`

**Check**: Look at browser Network tab
- Request URL should match your backend route exactly
- Common mismatch: `/auth/login` vs `/api/auth/login`

**Fix**: Verify route paths match between frontend and backend

### 3. ❌ Backend is Down/Not Deployed

**Problem**: Railway backend not running or crashed

**Check**:
```bash
curl https://YOUR-BACKEND.railway.app/health

# If returns HTML or error → Backend is down!
# Expected: {"status":"healthy"}
```

**Fix**: Deploy/restart Railway backend

### 4. ❌ CORS Preflight Returning HTML

**Problem**: CORS OPTIONS request returns HTML error page

**Check**: Browser console for CORS errors

**Fix**: Configure CORS in Railway backend

---

## ✅ Step-by-Step Diagnosis

### Step 1: Check What URL Frontend is Calling

1. **Open your Vercel app**: https://q4-hackathon2-todo-fullstack.vercel.app
2. **Open DevTools**: Press F12
3. **Go to Network tab**
4. **Try to login**
5. **Click on the failed request**
6. **Look at "General" → "Request URL"**

**What do you see?**

#### Scenario A: Request URL is `http://localhost:8000/...`
❌ **Problem**: Environment variable not set
✅ **Fix**: Set `NEXT_PUBLIC_API_URL` in Vercel (see below)

#### Scenario B: Request URL is `https://something.railway.app/...`
✅ Good - but check the response...

---

### Step 2: Check What the Backend Returns

1. **In Network tab, click the failed request**
2. **Go to "Response" tab**
3. **Look at the response body**

**What do you see?**

#### Response A: HTML Page (<!DOCTYPE html>...)
❌ **Problem**: Backend returning error page, not JSON

**Common reasons**:
- 404 Not Found (wrong endpoint)
- 500 Server Error (backend crashed)
- CORS error (preflight failed)

**Check the status code**:
- 404 → Wrong endpoint URL
- 500 → Backend error (check Railway logs)
- 503 → Backend is down

#### Response B: JSON Error
✅ Backend is working, but returns an error
- Check the error message in the JSON
- Might be validation error, auth error, etc.

---

## 🛠️ Fix #1: Set NEXT_PUBLIC_API_URL in Vercel

**This is the #1 cause of this error!**

### Find Your Railway Backend URL

**Option A: Check Railway Dashboard**
1. Go to: https://railway.app/
2. Open your backend project
3. Copy the public URL (e.g., `https://web-production-XXXX.railway.app`)

**Option B: Test if you have a working backend**
```bash
# Try common Railway URL patterns (replace with your project)
curl https://q4-hackathon2-todo-backend.railway.app/health
curl https://web-production-XXXX.railway.app/health

# Expected: {"status":"healthy"}
```

### Set the Environment Variable

1. **Go to Vercel**: https://vercel.com/ → Your project → Settings → Environment Variables

2. **Add or Update**:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://YOUR-BACKEND.railway.app` ← **YOUR ACTUAL RAILWAY URL**
   - **Environments**: ✅ Production, ✅ Preview, ✅ Development

3. **Save**

### Redeploy Vercel

1. Deployments tab → Latest deployment
2. Click "..." → "Redeploy"
3. Wait 1-2 minutes

---

## 🛠️ Fix #2: Verify Backend Routes

### Check Your Backend Routes

1. **Test health endpoint**:
```bash
curl https://YOUR-BACKEND.railway.app/health

# Expected: {"status":"healthy"}
# If HTML: Backend route is wrong or not set up
```

2. **Test auth endpoints**:
```bash
# Test login endpoint
curl https://YOUR-BACKEND.railway.app/auth/login

# Should return JSON error (not HTML):
# {"detail": "Method not allowed"} or similar
```

### Common Route Mismatches

**Frontend might call**: `/api/auth/login`
**Backend might expect**: `/auth/login`

**Check your backend main.py**:
```python
# In phase2-fullstack/backend/app/main.py
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# ↑ This means routes are at /auth/*, not /api/auth/*
```

**If mismatch**: Update frontend proxy route configuration

---

## 🛠️ Fix #3: Check Railway Backend Logs

If backend URL is correct but still returns HTML:

1. **Go to Railway**: https://railway.app/ → Your backend service
2. **Click on "Deployments"**
3. **Click latest deployment**
4. **Click "View Logs"**

**Look for**:
- ❌ Crash errors (Python exceptions)
- ❌ Database connection errors
- ❌ Missing environment variables
- ❌ Port binding errors

**Common issues**:
```
# Missing DATABASE_URL
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL

# Missing SECRET_KEY
KeyError: 'SECRET_KEY'

# Wrong port
Address already in use: 0.0.0.0:8000
```

---

## 🧪 Testing Commands

Run these to diagnose:

### Test 1: Backend Health
```bash
curl https://YOUR-BACKEND.railway.app/health
# Expected: {"status":"healthy"}
```

### Test 2: Backend Auth Routes
```bash
# Should return JSON error (405 Method Not Allowed), not HTML
curl https://YOUR-BACKEND.railway.app/auth/login
```

### Test 3: Backend Register (Should Work)
```bash
curl -X POST https://YOUR-BACKEND.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"TestPass123"}'

# Expected: JSON with tokens or error
# NOT: HTML page
```

### Test 4: Frontend Proxy
```bash
# From browser console on Vercel site
fetch('/api/auth/verify')
  .then(r => r.text())
  .then(console.log)

// Should show JSON or JSON error
// NOT: <!DOCTYPE html>
```

---

## 📋 Complete Troubleshooting Checklist

Work through these in order:

### Vercel Frontend
- [ ] `NEXT_PUBLIC_API_URL` is set in Vercel environment variables
- [ ] Value is correct Railway backend URL (starts with https://)
- [ ] All three environments checked (Production, Preview, Development)
- [ ] Redeployed after setting variable
- [ ] Build logs show: `NEXT_PUBLIC_API_URL: https://...railway.app`
- [ ] Browser Network tab shows requests going to Railway URL

### Railway Backend
- [ ] Backend is deployed and running
- [ ] Health endpoint works: `curl https://YOUR-BACKEND.railway.app/health`
- [ ] Returns JSON: `{"status":"healthy"}`
- [ ] Environment variables set: DATABASE_URL, SECRET_KEY, CORS_ORIGINS
- [ ] No errors in deployment logs
- [ ] Routes are configured: `/auth/login`, `/auth/register`, etc.

### API Routes Match
- [ ] Frontend calls match backend routes
- [ ] If frontend calls `/api/auth/login`, backend has that route
- [ ] If backend has `/auth/login`, frontend proxy forwards correctly
- [ ] No extra `/api/` prefix mismatches

### CORS Configuration
- [ ] Railway `CORS_ORIGINS` includes Vercel domain
- [ ] Value: `http://localhost:3000,https://q4-hackathon2-todo-fullstack.vercel.app`
- [ ] No CORS errors in browser console
- [ ] Preflight OPTIONS requests succeed

---

## 🎯 Quick Fix Summary

**99% of the time, it's one of these**:

### Fix A: Set Backend URL in Vercel
```
Vercel → Settings → Environment Variables
Add: NEXT_PUBLIC_API_URL = https://YOUR-BACKEND.railway.app
Then: Redeploy
```

### Fix B: Backend is Down
```
Railway → Check deployment logs
Fix errors and redeploy
```

### Fix C: Route Mismatch
```
Check frontend calls match backend routes
Update proxy configuration if needed
```

---

## 🔍 How to Know Which Fix You Need

### See this in browser Network tab?
**Request URL: `http://localhost:8000/...`**
→ Fix A: Set `NEXT_PUBLIC_API_URL`

**Response: HTML page with "404 Not Found"**
→ Fix C: Route mismatch

**Response: HTML page with "500 Internal Server Error"**
→ Fix B: Backend is down/crashed

**Status: 503 Service Unavailable**
→ Fix B: Backend not running

---

## 🆘 Still Getting HTML Instead of JSON?

If you've tried everything, provide these:

1. **Your Railway backend URL**: `https://...`
2. **Browser Network tab screenshot** showing:
   - Request URL
   - Response tab with HTML content
   - Status code
3. **Railway deployment logs** (last 50 lines)
4. **Vercel environment variables** (screenshot)
5. **Output of these commands**:
   ```bash
   curl https://YOUR-BACKEND.railway.app/health
   curl https://YOUR-BACKEND.railway.app/auth/login
   ```

---

## ✅ Expected Result After Fix

### Before Fix:
```
Request: /api/auth/login
Response: <!DOCTYPE html>...
Error: Unexpected token '<'
```

### After Fix:
```
Request: /api/auth/login
Response: {"access_token":"...","token_type":"bearer"}
Success: Login works!
```

---

## 📖 Related Guides

- **Quick Fix**: FIX_VERCEL_AUTH_ERROR.md
- **Complete Setup**: phase2-fullstack/frontend/VERCEL_SETUP.md
- **Debugging**: DEBUGGING_VERCEL_ERRORS.md
