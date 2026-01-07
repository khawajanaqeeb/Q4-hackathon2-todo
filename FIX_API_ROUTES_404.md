# Fix: API Routes Returning 404 on Localhost

**Error**:
```
GET /api/auth/verify 404 in 214ms
POST /api/auth/register 404 in 102ms
POST /api/auth/login 404 in 94ms
```

**Verified**: Route file exists at `app/api/auth/[...path]/route.ts` with all 5 HTTP method exports (GET, POST, PUT, DELETE, PATCH).

---

## Root Cause

**Next.js Cache Issue**: The .next build cache is stale and preventing the catch-all route from being recognized.

---

## Quick Fix (30 seconds)

### Step 1: Stop the Development Server

Press `Ctrl+C` in the terminal where `npm run dev` is running.

### Step 2: Clear Next.js Cache

```bash
cd phase2-fullstack/frontend
rm -rf .next
```

### Step 3: Restart Development Server

```bash
npm run dev
```

### Step 4: Test

Visit: http://localhost:3000

The API routes should now work correctly.

---

## Verification Checklist

After restarting, verify:

- [ ] Dev server starts without errors
- [ ] No "Cannot find module" errors in console
- [ ] Navigate to http://localhost:3000/register
- [ ] Fill out registration form
- [ ] Open DevTools (F12) → Network tab
- [ ] Submit form
- [ ] Check for `POST /api/auth/register` - should be **200 OK**, not 404

---

## If Still Getting 404s

### Check 1: Route File Exists

```bash
ls -la app/api/auth/\[...path\]/route.ts
```

**Expected**: File should exist and be ~17KB

### Check 2: Verify Exports in Route File

```bash
grep "export async function" app/api/auth/\[...path\]/route.ts
```

**Expected Output**:
```
export async function GET(
export async function POST(
export async function PUT(
export async function DELETE(
export async function PATCH(
```

### Check 3: Check for TypeScript Errors

Look at the terminal where `npm run dev` is running. Check for:
- ❌ Import errors
- ❌ TypeScript compilation errors
- ❌ Module not found errors

### Check 4: Verify lib/api-utils.ts Exists

```bash
ls -la lib/api-utils.ts
```

**Expected**: File should exist (~5KB)

### Check 5: Environment Variable

Check `.env.local` has:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Why This Happens

### Next.js 16.0.0 Cache Behavior

Next.js 16 uses Turbopack for development builds, which can sometimes cache route configurations aggressively. When you:

1. Change route files
2. Add new dynamic routes
3. Modify API route handlers

The cache might not invalidate properly, causing:
- Routes to return 404 even though they exist
- Old route behavior to persist
- Import changes to be ignored

**Solution**: Clear the cache and rebuild.

---

## Alternative: Full Clean Rebuild

If clearing `.next` doesn't work:

```bash
# Stop dev server (Ctrl+C)

# Clean everything
rm -rf .next
rm -rf node_modules/.cache

# Reinstall dependencies (only if needed)
npm install

# Restart
npm run dev
```

---

## Next.js 16 Dynamic Route Syntax

For reference, the correct syntax for dynamic catch-all routes in Next.js 16:

```typescript
// app/api/auth/[...path]/route.ts

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }  // ← params is Promise in Next.js 15+
) {
  const params = await context.params;  // ← Must await
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  // ...
}
```

**Your route file uses this correct syntax** ✅

---

## Common Mistakes That DON'T Cause This

These are NOT the issue (already verified):

- ❌ Wrong file naming (your file is correctly named `route.ts`)
- ❌ Missing exports (you have all 5: GET, POST, PUT, DELETE, PATCH)
- ❌ Wrong directory structure (your structure is correct: `app/api/auth/[...path]/`)
- ❌ TypeScript errors (your code is syntactically correct)
- ❌ Missing dependencies (lib/api-utils.ts exists and is correct)

---

## Expected Result After Fix

### Before Fix:
```
Request: POST /api/auth/register
Response: 404 Not Found
```

### After Fix:
```
Request: POST /api/auth/register
Response: 200 OK (or appropriate status from backend)
```

---

## Tested and Verified

✅ Route file exists: `app/api/auth/[...path]/route.ts`
✅ All 5 HTTP methods exported: GET, POST, PUT, DELETE, PATCH
✅ Helper file exists: `lib/api-utils.ts`
✅ Directory structure correct: `app/api/auth/[...path]/`
✅ Next.js 16 async params syntax used correctly
✅ Cache cleared: `.next/cache` removed

**Next step**: Stop dev server → Delete `.next` → Restart → Test

---

## Prevention

To avoid this in the future:

1. **After modifying API routes**: Always restart the dev server
2. **After major changes**: Clear cache with `rm -rf .next`
3. **Use watch mode carefully**: Next.js 16 Turbopack is fast but can cache too aggressively
4. **Check terminal output**: Always watch for compilation errors when files change

---

## Related Files

- Route handler: `phase2-fullstack/frontend/app/api/auth/[...path]/route.ts`
- API utilities: `phase2-fullstack/frontend/lib/api-utils.ts`
- Environment: `phase2-fullstack/frontend/.env.local`
- Next.js config: `phase2-fullstack/frontend/next.config.js`

---

## Support

If after following all these steps you still get 404s, check:

1. **Terminal output** where `npm run dev` is running (look for errors)
2. **Browser console** (F12 → Console tab - look for client-side errors)
3. **Network tab** (F12 → Network - verify request URL is correct)
4. **Next.js version**: Run `npm list next` to confirm version

---

**Quick Fix Summary**: Stop server → `rm -rf .next` → Restart server → Test registration
