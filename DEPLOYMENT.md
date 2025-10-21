# Deployment Guide for Sevalla

## Prerequisites
- GitHub repository with your code pushed
- Sevalla account (https://app.sevalla.com/)

## Step 1: Create PostgreSQL Database on Sevalla

1. **Log in to Sevalla Dashboard**
   - Go to https://app.sevalla.com/
   - Click "New +" button
   - Select "PostgreSQL"

2. **Configure Database**
   - Name: `string-analyzer-db`
   - Database: `string_analyzer`
   - User: (auto-generated or custom)
   - Region: Choose closest to your users
   - Plan: Select appropriate plan

3. **Save Database Credentials**
   After creation, you'll get:
   ```
   Internal Database URL: postgresql://user:password@host:5432/database
   External Database URL: postgresql://user:password@external-host:5432/database
   ```
   
   Save the **Internal Database URL** - you'll need it!

## Step 2: Deploy Your Application

1. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"

2. **Connect Repository**
   - Connect your GitHub account
   - Select repository: `Olaitan34/string-analyzer-api`
   - Branch: `main`

3. **Configure Build Settings**
   
   **Basic Settings:**
   - Name: `string-analyzer-api`
   - Region: Same as database
   - Branch: `main`
   - Root Directory: (leave empty)
   
   **Build Command:**
   ```bash
   chmod +x build.sh && ./build.sh
   ```
   
   **Start Command:**
   ```bash
   gunicorn string_analyzer.wsgi:application --bind 0.0.0.0:$PORT
   ```

4. **Set Environment Variables**
   
   Click "Environment" tab and add:
   
   ```
   SECRET_KEY=your-generated-secret-key-here-50-characters-minimum
   DEBUG=False
   ALLOWED_HOSTS=.sevalla.app,.onrender.com,your-custom-domain.com
   DATABASE_URL=postgresql://user:password@internal-host:5432/database
   CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
   ```
   
   **Generate SECRET_KEY:**
   Run locally:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)

## Step 3: Verify Deployment

1. **Check Build Logs**
   - Monitor the deployment logs
   - Ensure migrations run successfully
   - Check for any errors

2. **Test Your API**
   
   Your API will be available at: `https://your-app-name.sevalla.app/api/`
   
   Test endpoints:
   ```bash
   # Create a string
   curl -X POST https://your-app-name.sevalla.app/api/strings/ \
     -H "Content-Type: application/json" \
     -d '{"value": "racecar"}'
   
   # List strings
   curl https://your-app-name.sevalla.app/api/strings/
   ```

## Step 4: Custom Domain (Optional)

1. In Sevalla Dashboard, go to your web service
2. Click "Settings" → "Custom Domain"
3. Add your domain: `api.yourdomain.com`
4. Update DNS records as instructed
5. Update `ALLOWED_HOSTS` in environment variables

## Troubleshooting

### Issue: Static files not loading
**Solution:** Run build command manually:
```bash
python manage.py collectstatic --no-input
```

### Issue: Database connection failed
**Solution:** 
- Verify DATABASE_URL is correct
- Use **Internal Database URL** (not external)
- Ensure database and web service are in same region

### Issue: 500 Internal Server Error
**Solution:**
- Check logs in Sevalla Dashboard
- Verify all environment variables are set
- Ensure DEBUG=False in production

### Issue: CORS errors
**Solution:**
- Update CORS_ALLOWED_ORIGINS with your frontend domain
- Include both http and https if needed

## Monitoring

1. **View Logs**
   - Go to your web service in Sevalla
   - Click "Logs" tab
   - Monitor real-time logs

2. **Check Health**
   - Visit: `https://your-app-name.sevalla.app/admin/`
   - Should see Django admin login

## Updating Your App

To deploy updates:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Sevalla will automatically detect changes and redeploy.

## Production Checklist

- [ ] PostgreSQL database created
- [ ] SECRET_KEY generated and set
- [ ] DEBUG set to False
- [ ] ALLOWED_HOSTS configured
- [ ] DATABASE_URL set to Internal Database URL
- [ ] CORS_ALLOWED_ORIGINS configured
- [ ] Build script runs successfully
- [ ] Migrations completed
- [ ] Static files collected
- [ ] All endpoints tested
- [ ] SSL/HTTPS working

## Your API Endpoints

Once deployed, your endpoints will be:

```
POST   https://your-app.sevalla.app/api/strings/
GET    https://your-app.sevalla.app/api/strings/
GET    https://your-app.sevalla.app/api/strings/{value}/
DELETE https://your-app.sevalla.app/api/strings/{value}/
GET    https://your-app.sevalla.app/api/strings/filter-by-natural-language/
```

## Support

- Sevalla Docs: https://docs.sevalla.com/
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/

---

**Note:** Sevalla offers free tier with limitations. For production apps, consider paid plans for better performance.
