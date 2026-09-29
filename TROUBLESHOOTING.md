# Sherlock.ai Frontend Blank Page - Troubleshooting Guide

## Issues Found and Fixed

### 1. ❌ Missing TypeScript Configuration
**Problem:** No `tsconfig.json` or `tsconfig.node.json` files
**Status:** ✅ FIXED - Created both configuration files

### 2. ❌ Missing TypeScript Type Definitions
**Problem:** Missing `@types/react` and `@types/react-dom` packages
**Status:** ✅ FIXED - Updated package.json with required types and TypeScript

### 3. ⚠️ Package.json Issues
**Problem:** 
- Missing "type": "module" field
- Name had spaces (should be kebab-case)
- Using wildcard (*) for some dependencies
**Status:** ✅ FIXED - Updated package.json

## Steps to Fix the Blank Page

### Step 1: Reinstall Dependencies
```bash
cd D:\Sherlock.ai\frontend
npm install
```

This will install:
- TypeScript (v5.6.3)
- @types/react (v18.3.12)
- @types/react-dom (v18.3.1)
- All updated dependencies

### Step 2: Check for Console Errors

Open your browser's Developer Tools (F12) and check:

1. **Console Tab** - Look for JavaScript errors:
   - Module resolution errors
   - Import errors
   - Component rendering errors

2. **Network Tab** - Check if files are loading:
   - main.tsx
   - App.tsx
   - CSS files
   - Component files

### Step 3: Common Issues to Check

#### A. CORS Issues with Backend
If you see CORS errors, update your backend's `app.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### B. Port Conflicts
- Frontend runs on: http://localhost:3000
- Backend should run on: http://127.0.0.1:8000
- Make sure both ports are available

#### C. Missing Dependencies
Run this to check for missing peer dependencies:
```bash
npm list
```

### Step 4: Start the Application

```bash
# Terminal 1 - Start Backend
cd D:\Sherlock.ai\backend
python app.py

# Terminal 2 - Start Frontend  
cd D:\Sherlock.ai\frontend
npm run dev
```

### Step 5: Debug Mode

If the page is still blank, use the debug version:

1. Temporarily edit `index.html` to use the debug main file:
```html
<script type="module" src="/src/main-debug.tsx"></script>
```

2. Check the console for specific error messages

## What Should Happen

When working correctly:
1. Browser opens automatically to http://localhost:3000
2. You see the Sherlock.ai homepage with:
   - Large "SHERLOCK.AI" title
   - "AI that watches AI" subtitle
   - "Detect Image" and "Detect Video" buttons
   - Dark Ferrari-style background

## Still Having Issues?

### Check Browser Console
Press F12 and look for:
- Red error messages
- Failed module imports
- 404 errors for missing files

### Common Error Messages and Solutions

**"Failed to resolve module"**
→ Run `npm install` again

**"Cannot find module './components/...'"**
→ Check that all component files exist in src/components/

**"Unexpected token '<'"**
→ TypeScript compilation error - check tsconfig.json

**"Module parse failed"**
→ Vite configuration issue - check vite.config.ts

**White/Blank screen with no console errors**
→ CSS not loading - check index.css import in main.tsx

## Verify File Structure

Your frontend should have:
```
frontend/
├── index.html ✅
├── package.json ✅ (updated)
├── tsconfig.json ✅ (created)
├── tsconfig.node.json ✅ (created)
├── vite.config.ts ✅
└── src/
    ├── main.tsx ✅
    ├── App.tsx ✅
    ├── index.css ✅
    ├── api/
    │   └── sherlockApi.ts ✅
    └── components/
        ├── Hero.tsx ✅
        ├── Navigation.tsx ✅
        ├── ImageDetection.tsx ✅
        ├── VideoDetection.tsx ✅
        ├── About.tsx ✅
        └── ui/ ✅
```

## Next Steps After Fixing

1. Test image detection functionality
2. Test video detection functionality
3. Check API connectivity with backend
4. Verify Trust Score calculations

## Backend Connection Test

Once frontend loads, test the API:
```bash
curl http://127.0.0.1:8000/
```

Should return backend info or docs URL.
