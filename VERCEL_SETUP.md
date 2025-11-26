# Vercel Deployment Environment Variables

## ⚠️ CRITICAL: Required Environment Variables for Vercel

You must configure these environment variables in your Vercel dashboard for the application to work properly.

### How to Add Environment Variables in Vercel:

1. Go to https://vercel.com/dashboard
2. Select your project: `ansa-deco-glass`
3. Go to **Settings** → **Environment Variables**
4. Add each variable below with the correct value

---

## Required Variables

### 1. Flask Configuration

```
SECRET_KEY=generate-a-random-secure-key-here-use-python-secrets
```
**How to generate:** Run `python -c "import secrets; print(secrets.token_hex(32))"`

```
FLASK_ENV=production
```

---

### 2. Supabase Configuration (CRITICAL)

```
SUPABASE_URL=https://fovexourytgwrvrvlbbs.supabase.co
```

```
SUPABASE_KEY=your-supabase-anon-public-key
```

```
SUPABASE_SERVICE_KEY=your-supabase-service-role-key
```

**Where to find these:**
- Go to your Supabase project: https://supabase.com/dashboard/project/fovexourytgwrvrvlbbs
- Click **Settings** → **API**
- Copy the `URL`, `anon/public key`, and `service_role key`

---

### 3. Login Credentials (CRITICAL FOR ADMIN ACCESS)

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourSecurePassword123!
```

```
HR_USERNAME=hr_admin
HR_PASSWORD=YourSecurePassword123!
```

```
MEDICAL_USERNAME=medical_admin
MEDICAL_PASSWORD=YourSecurePassword123!
```

```
SAFETY_USERNAME=safety_admin
SAFETY_PASSWORD=YourSecurePassword123!
```

**⚠️ IMPORTANT:** Change the default passwords! These are used for login authentication.

---

### 4. Security Settings

```
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

---

### 5. Optional Configuration

```
COMPANY_NAME=ANSA Deco Glass
COMPANY_ADDRESS=Manufacturing Unit, Industrial Area
COMPANY_LOGO=static/images/COMPANY_LOGO.png
IDCARD_VALIDITY_DAYS=365
MAX_CONTENT_LENGTH=16777216
```

---

## Vercel Environment Variables Checklist

After adding variables, verify these are set in Vercel:

- [ ] `SECRET_KEY` - Flask secret key for sessions
- [ ] `SUPABASE_URL` - Your Supabase project URL
- [ ] `SUPABASE_KEY` - Supabase anon/public key
- [ ] `SUPABASE_SERVICE_KEY` - Supabase service role key
- [ ] `ADMIN_USERNAME` - Admin login username
- [ ] `ADMIN_PASSWORD` - Admin login password
- [ ] `HR_USERNAME` - HR login username
- [ ] `HR_PASSWORD` - HR login password
- [ ] `MEDICAL_USERNAME` - Medical officer username
- [ ] `MEDICAL_PASSWORD` - Medical officer password
- [ ] `SAFETY_USERNAME` - Safety officer username
- [ ] `SAFETY_PASSWORD` - Safety officer password

---

## After Setting Environment Variables

1. **Redeploy the application:**
   - Go to Vercel Dashboard → Deployments
   - Click on the latest deployment
   - Click "Redeploy"
   
2. **Test login:**
   - Visit your site: https://ansa-deco-glass.vercel.app/admin/login
   - Use the credentials you set in `ADMIN_USERNAME` and `ADMIN_PASSWORD`

---

## Troubleshooting Login Issues

### Issue: "Invalid credentials" on Vercel but works locally

**Cause:** Environment variables not set in Vercel

**Solution:**
1. Check Vercel Dashboard → Settings → Environment Variables
2. Ensure `ADMIN_USERNAME` and `ADMIN_PASSWORD` are set
3. Redeploy after adding variables

### Issue: Login form doesn't submit

**Cause:** Session cookies not working

**Solution:**
1. Ensure `SECRET_KEY` is set in Vercel
2. Check that `SESSION_COOKIE_SECURE=True` (required for HTTPS)
3. Clear browser cookies and try again

### Issue: Can't see environment variables working

**Cause:** Need to redeploy after adding variables

**Solution:**
1. After adding/changing any environment variable
2. Must redeploy: Dashboard → Deployments → Redeploy
3. Variables are only available after redeployment

---

## Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore` for a reason
2. **Use strong passwords** - Don't use default `admin@123`, `hr@123`, etc.
3. **Rotate SECRET_KEY** - Generate a new one for production
4. **Limit service key access** - Only use in server-side code, never expose to client

---

## Need Help?

1. Check Vercel logs: Dashboard → Deployments → Click deployment → View Function Logs
2. Look for error messages related to environment variables
3. Verify all required variables are present in Settings → Environment Variables
