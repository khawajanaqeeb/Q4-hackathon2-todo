# ✅ Railway Backend Found - Final Configuration Steps

**Your Railway Backend URL**: `https://q4-hackathon2-todo-production.up.railway.app`

**Status**: ✅ Backend is running and returning JSON!

---

## 🧪 Test Your Backend

Run these commands to verify everything works:

### 1. Test Health Endpoint
```bash
curl https://q4-hackathon2-todo-production.up.railway.app/health
```

**Expected Response**:
```json
{"status":"healthy"}
```

### 2. Test Auth Route Exists
```bash
curl https://q4-hackathon2-todo-production.up.railway.app/auth/login
```

**Expected Response** (Method Not Allowed is OK):
```json
{"detail":"Method Not Allowed"}
```

### 3. Test Registration Endpoint
```bash
curl -X POST https://q4-hackathon2-todo-production.up.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"TestPass123!"}'
```

**Expected Response** (tokens or email already exists):
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

## 🎯 Now Configure Vercel (3 Steps)

### Step 1: Set Environment Variable in Vercel

1. **Go to Vercel Dashboard**:
   https://vercel.com/ → Your project → Settings → Environment Variables

2. **Click "Add New Variable"**

3. **Enter**:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://q4-hackathon2-todo-production.up.railway.app`
   - **Environments**: ✅ Production, ✅ Preview, ✅ Development

4. **Click "Save"**

---

### Step 2: Configure CORS in Railway

Your backend needs to allow requests from your Vercel frontend.

1. **Go to Railway Dashboard**:
   https://railway.app/ → Your backend service → Variables

2. **Find or Add** the `CORS_ORIGINS` variable

3. **Set the value to** (copy-paste this exactly):
   ```
   http://localhost:3000,https://q4-hackathon2-todo-fullstack.vercel.app,https://q4-hackathon2-todo-fullstack-*.vercel.app
   ```

4. **Click "Add" or "Update"**

5. **Railway will automatically redeploy** (wait 1-2 minutes)

---

### Step 3: Redeploy Vercel

**IMPORTANT**: Environment variables only work in NEW deployments!

1. **Go to Vercel**:
   https://vercel.com/ → Your project → Deployments

2. **Click "..." menu** on latest deployment (top of list)

3. **Click "Redeploy"**

4. **Wait 1-2 minutes** for deployment to complete

---

## ✅ Test the Complete Flow

After both services redeploy:

1. **Visit your Vercel app**:
   https://q4-hackathon2-todo-fullstack.vercel.app

2. **Hard refresh** your browser:
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

3. **Open DevTools** (F12) → **Network** tab

4. **Try to register a new account**:
   - Name: Your Name
   - Email: your@email.com
   - Password: YourPassword123!

5. **Check Network tab**:
   - Request URL should be: `https://q4-hackathon2-todo-production.up.railway.app/auth/register`
   - Status should be: **200 OK**
   - Response should have: `access_token` and `refresh_token`

6. **Expected Result**:
   - ✅ Registration succeeds
   - ✅ You're logged in automatically
   - ✅ Redirected to dashboard
   - ✅ Can create/view/edit todos

---

## 🔍 Verification Checklist

Before testing, verify:

### Vercel Settings
- [ ] Go to: https://vercel.com/ → Settings → Environment Variables
- [ ] `NEXT_PUBLIC_API_URL` exists
- [ ] Value is: `https://q4-hackathon2-todo-production.up.railway.app`
- [ ] All three environments checked (Production, Preview, Development)
- [ ] You clicked "Save"

### Railway Settings
- [ ] Go to: https://railway.app/ → Backend service → Variables
- [ ] `CORS_ORIGINS` exists
- [ ] Value includes: `https://q4-hackathon2-todo-fullstack.vercel.app`
- [ ] Full value is: `http://localhost:3000,https://q4-hackathon2-todo-fullstack.vercel.app,https://q4-hackathon2-todo-fullstack-*.vercel.app`
- [ ] Backend redeployed after change

### Deployments
- [ ] Vercel shows new deployment in progress/completed
- [ ] Railway shows "Active" status
- [ ] Waited 2-3 minutes for both to finish
- [ ] Hard refreshed browser after deployments complete

---

## 🎯 Quick Reference

### Your URLs
- **Backend (Railway)**: `https://q4-hackathon2-todo-production.up.railway.app`
- **Frontend (Vercel)**: `https://q4-hackathon2-todo-fullstack.vercel.app`

### Environment Variables

**Vercel** (`NEXT_PUBLIC_API_URL`):
```
https://q4-hackathon2-todo-production.up.railway.app
```

**Railway** (`CORS_ORIGINS`):
```
http://localhost:3000,https://q4-hackathon2-todo-fullstack.vercel.app,https://q4-hackathon2-todo-fullstack-*.vercel.app
```

---

## 🧪 Backend Health Check Commands

Keep these handy for testing:

```bash
# Health endpoint
curl https://q4-hackathon2-todo-production.up.railway.app/health

# Test registration
curl -X POST https://q4-hackathon2-todo-production.up.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"Test123!"}'

# Test login
curl -X POST https://q4-hackathon2-todo-production.up.railway.app/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123!"
```

---

## 🚨 Troubleshooting

### Still Getting Errors?

**Error: "Authentication service unavailable"**
- Check: Did you redeploy Vercel after setting env var?
- Check: Browser Network tab shows Railway URL (not localhost)?

**Error: "CORS policy"**
- Check: `CORS_ORIGINS` in Railway includes your Vercel domain?
- Check: Railway backend redeployed after CORS change?

**Error: "Unexpected token '<'"**
- Check: Environment variable `NEXT_PUBLIC_API_URL` is set?
- Check: Value doesn't have trailing slash?
- Check: Vercel build logs show the correct URL?

### View Logs

**Vercel Logs**:
1. Vercel → Deployments → Latest → Functions
2. Look for errors

**Railway Logs**:
1. Railway → Backend service → Deployments → Latest
2. Click "View Logs"
3. Look for incoming requests and errors

---

## ✅ Expected Result

### Before Configuration:
```
Frontend: https://q4-hackathon2-todo-fullstack.vercel.app
   ↓
Backend: http://localhost:8000 ← DOESN'T EXIST
   ↓
Error: 503 Service Unavailable
```

### After Configuration:
```
Frontend: https://q4-hackathon2-todo-fullstack.vercel.app
   ↓
Backend: https://q4-hackathon2-todo-production.up.railway.app ✅
   ↓
Success: Authentication works! Todos work! 🎉
```

---

## 📊 Summary

| Task | Status | Action |
|------|--------|--------|
| Backend Running | ✅ YES | `https://q4-hackathon2-todo-production.up.railway.app` |
| Set Vercel Env Var | ⏳ DO NOW | Add `NEXT_PUBLIC_API_URL` |
| Set Railway CORS | ⏳ DO NOW | Add Vercel domain to `CORS_ORIGINS` |
| Redeploy Vercel | ⏳ AFTER | Redeploy to apply env var |
| Test Auth | ⏳ FINAL | Try login/register on Vercel site |

---

**Next Step**: Configure Vercel environment variable (Step 1 above), then Railway CORS (Step 2), then redeploy (Step 3)! 🚀
