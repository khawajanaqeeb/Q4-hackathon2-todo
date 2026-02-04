# Authentication Setup for Vercel Deployment

## Prerequisites
- Backend deployed on Railway with a public URL (e.g., `https://your-app.railway.app`)
- Vercel account and project set up

## Step 1: Configure Backend CORS Settings

On Railway, update your backend environment variables:

1. Go to your Railway project dashboard
2. Navigate to the "Variables" tab
3. Add/update the `CORS_ORIGINS` variable with the following value:
   ```
   http://localhost:3000,https://q4-hackathon2-todo-fullstack.vercel.app,https://q4-hackathon2-todo-fullstack-*.vercel.app
   ```
4. Save and redeploy your backend

## Step 2: Configure Frontend Environment Variables

In your Vercel dashboard:

1. Go to your Vercel project settings
2. Navigate to "Environment Variables"
3. Add the following variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: Your Railway backend URL (e.g., `https://your-app.railway.app`)
4. Make sure to enable this variable for Production, Preview, and Development environments

## Step 3: Redeploy

1. Trigger a new deployment in Vercel after setting the environment variables
2. Wait for the build to complete

## Verification

After deployment:

1. Visit your Vercel app URL
2. Open browser developer tools (F12)
3. Go to the Network tab
4. Try to register or login
5. Verify that requests are going to your Railway backend (not localhost)

## Troubleshooting

If authentication still fails:

1. Check that your Railway backend is healthy:
   ```bash
   curl https://your-railway-backend.railway.app/health
   ```
   
2. Verify CORS headers in browser Network tab - they should allow your Vercel domain

3. Check that the NEXT_PUBLIC_API_URL is correctly set in Vercel environment variables

4. Look for any error messages in browser console