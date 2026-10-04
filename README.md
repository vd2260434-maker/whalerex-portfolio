# Whalerex Portfolio & Admin Portal

Production-ready personal portfolio and creative studio website with a secure Admin Dashboard at `/admin`, prepared for Vercel deployment.

## Features
- **Portfolio Website**: Modern, high-performance responsive portfolio featuring the Whalerex logo opening animation, smooth parallax effects, interactive project card for Waffle House, and contact links.
- **Admin Dashboard (`/admin`)**:
  - Secure session-based authentication (HMAC-SHA256 tokens).
  - Protected admin routes.
  - Real-time contact inquiry management (view, reply, mark as read, delete).
  - Featured project link & metadata management.
  - Availability status and contact coordinates editor.
  - Responsive layout matching the portfolio design language.
- **Production Serverless Architecture**:
  - Zero external build dependencies.
  - Compatible with Vercel Serverless Functions (`api/*.js`).
  - Strict security headers (`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`).

---

## Environment Variables

Configure these in **Vercel Project Settings → Environment Variables**:

| Variable | Description | Example Placeholder |
| :--- | :--- | :--- |
| `ADMIN_USERNAME` | Administrator login username | `your_admin_username` |
| `ADMIN_PASSWORD` | Administrator login password | `your_secure_password` |
| `JWT_SECRET` | Cryptographic secret for signing session tokens | `your_random_secret` |

---

## Deploying to Vercel

### Option 1: Via GitHub (Recommended)
1. Push this folder to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Whalerex portfolio and admin dashboard"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/whalerex-portfolio.git
   git push -u origin main
   ```
2. Go to [vercel.com/new](https://vercel.com/new) and import the repository.
3. Add the `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `JWT_SECRET` environment variables.
4. Click **Deploy**. Vercel will instantly build and deploy your site with automatic HTTPS.

### Option 2: Via Vercel CLI
```bash
npm install -g vercel
vercel login
vercel --prod
```

---

## Local Development

Set the required environment variables:

```bash
# Linux / macOS
export ADMIN_USERNAME="your_admin_username"
export ADMIN_PASSWORD="your_secure_password"
export JWT_SECRET="your_random_secret"

# Windows (PowerShell)
$env:ADMIN_USERNAME="your_admin_username"
$env:ADMIN_PASSWORD="your_secure_password"
$env:JWT_SECRET="your_random_secret"
```

Run the local server:
```bash
python server.py 3000
```
- Portfolio: `http://localhost:3000`
- Admin Dashboard: `http://localhost:3000/admin`
