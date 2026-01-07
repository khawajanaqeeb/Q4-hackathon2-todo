# Quick Fix: "Authentication service unavailable" on Vercel

**Your Vercel URL**: https://q4-hackathon2-todo-fullstack.vercel.app/
**Error**: "Authentication service unavailable"
**Cause**: Frontend can't find backend (trying to connect to localhost instead of Railway)

---

## 🚨 Quick Fix (5 Minutes)

### Step 1: Get Your Railway Backend URL

You need your Railway backend URL. Find it here:

1. **Go to Railway**: https://railway.app/
2. **Open your backend project**
3. **Find the deployment URL**: Should look like `https://something.railway.app`

**Test if it's working**:
```bash
curl https://your-backend.railway.app/health

# Expected: {"status":"healthy"}
# If it fails, your backend isn't running!
```

---

### Step 2: Set Environment Variable in Vercel

1. **Go to Vercel Dashboard**:
   https://vercel.com/ → Your project → Settings → Environment Variables

2. **Add New Variable**:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-railway-backend.railway.app` ← **PASTE YOUR ACTUAL URL**
   - **Environments**: Check ALL three boxes (Production, Preview, Development)

3. **Click "Save"**

---

### Step 3: Redeploy Vercel

1. **Go to**: Deployments tab
2. **Find latest deployment** (top of the list)
3. **Click** the "..." menu
4. **Click "Redeploy"**
5. **Wait** 1-2 minutes for rebuild

---

### Step 4: Update Railway CORS (CRITICAL!)

Your Railway backend needs to allow requests from Vercel:

1. **Go to Railway**: https://railway.app/ → Your backend service → Variables

2. **Find or Add** `CORS_ORIGINS` variable:
   ```
   http://localhost:3000,https://q4-hackathon2-todo-fullstack.vercel.app,https://q4-hackathon2-todo-fullstack-*.vercel.app
   ```

3. **Save** and **Redeploy** backend if needed

---

### Step 5: Test

1. **Visit**: https://q4-hackathon2-todo-fullstack.vercel.app
2. **Try to login/register**
3. **Open DevTools** (F12) → Network tab
4. **Check**: Requests should go to `https://your-backend.railway.app` (NOT localhost!)

**Expected**: Authentication works! ✅

---

## 🔍 Still Not Working?

### Check 1: Railway Backend is Running
```bash
curl https://your-backend.railway.app/health
# Must return: {"status":"healthy"}
```

### Check 2: Vercel Environment Variable
- Go to Vercel → Settings → Environment Variables
- Verify `NEXT_PUBLIC_API_URL` exists
- Value should be `https://your-backend.railway.app` (YOUR actual URL)
- All three environments checked (Production, Preview, Development)

### Check 3: Did You Redeploy?
- Environment variables ONLY apply to NEW deployments
- You MUST redeploy after setting variables

### Check 4: CORS in Railway
- Railway → Backend service → Variables
- `CORS_ORIGINS` must include: `https://q4-hackathon2-todo-fullstack.vercel.app`

### Check 5: Browser Console Errors
- F12 → Console tab
- Look for errors mentioning CORS or network failures
- Network tab should show requests to Railway (not localhost)

---

## 📖 Detailed Guides

If you need more help:

- **Frontend Setup**: `phase2-fullstack/frontend/VERCEL_SETUP.md`
- **Backend Setup**: `phase2-fullstack/backend/RAILWAY_SETUP.md`
- **Environment Variables**: `phase2-fullstack/frontend/.env.production.example`

---

## ✅ Checklist

Before asking for help, verify:

- [ ] I have my Railway backend URL
- [ ] Railway backend `/health` endpoint returns `{"status":"healthy"}`
- [ ] Vercel environment variable `NEXT_PUBLIC_API_URL` is set to my Railway URL
- [ ] I've redeployed Vercel after setting the environment variable
- [ ] Railway `CORS_ORIGINS` includes my Vercel domain
- [ ] Browser Network tab shows requests going to Railway (not localhost)
- [ ] I've cleared my browser cache and tried again

---

## 🎯 Expected Result

### Before Fix:
```
Frontend: https://q4-hackathon2-todo-fullstack.vercel.app
   ↓
Backend:  http://localhost:8000 ← DOESN'T EXIST!
   ↓
Error:    "Authentication service unavailable"
```

### After Fix:
```
Frontend: https://q4-hackathon2-todo-fullstack.vercel.app
   ↓
Backend:  https://your-backend.railway.app ← CORRECT!
   ↓
Result:   Authentication works! 🎉
```

---

**If you've followed all steps and it still doesn't work**, provide:
1. Your Railway backend URL
2. Screenshot of Vercel environment variables
3. Screenshot of Railway environment variables
4. Browser console errors (F12 → Console tab)
5. Network tab showing the failed request
