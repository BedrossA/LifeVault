# Login, Register & Auth Flow – Analysis and Fixes

**Date:** 2026-01-26  
**Scope:** Terminal logs (809–1019), `backend/` and `web/` code.

---

## 1. Terminal log summary

### 1.1 Login (401 Unauthorized)

- **Requests:** `POST /api/v1/auth/login` with `username` = `elonmu`, `olaherou1`, `usertest`.
- **Result:** All return **401** with `"Incorrect username or password"`.
- **SQL:** Single `SELECT ... FROM users WHERE users.username = %(username_1)s`; no email fallback query in logs.
- **Conclusion:** Users are found by username → password verification fails → 401. The earlier run had reset `elonmu` to `TestPass123!`; if that password isn’t used (or there’s encoding/trimming mismatch), verify fails.

### 1.2 Register and OPTIONS

- **OPTIONS /api/v1/auth/register:** Several **400 Bad Request** (e.g. from `192.168.0.106:63022`), then **200 OK** (e.g. from `192.168.0.106:59600`).
- **POST /register:** Username `olalaherou1`, email `lopebeuhouye-4406@yopmail.com` → **400** `"Email already registered"` (that email belongs to `olaherou12`). So register handler works; the problem was duplicate email.

---

## 2. Backend (`backend/`)

### 2.1 Auth flow (`app/api/v1/endpoints/auth.py`)

- **Login:** Uses `OAuth2PasswordRequestForm`. Username/password are stripped. Lookup: by `username` then by `email` if not found. `verify_password` via bcrypt; on failure we 401.
- **Register:** Uses `UserCreate`. Username, email, password are trimmed; email lowercased. Duplicate username/email → 400.
- **DB:** `get_db` logs `"Database session error: ..."` on any exception (including 401 from auth) and rolls back. The 401 is raised by auth, not by DB.

### 2.2 Config (`app/core/config.py`)

- **DEBUG:** Default `False`. Login debug logs (`Login verify: user_id=... verify_ok=...`) only when `DEBUG=True`.
- **CORS_ORIGINS:** Default list includes `http://localhost:5173`, `http://192.168.0.106:5173`, etc.

### 2.3 Dependencies (`app/core/deps.py`)

- **OAuth2PasswordBearer** `tokenUrl="/api/v1/auth/login"` is used only for protected routes. Login does **not** use it; it uses the form. So token URL config doesn’t affect login itself.

### 2.4 CORS and OPTIONS

- **CORSMiddleware:** `allow_origins`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
- **OPTIONS 400:** Preflight for `/api/v1/auth/*` sometimes returned 400. CORSMiddleware normally handles OPTIONS and returns 200; 400 suggests either a misconfiguration or an edge case (e.g. origin/headers). An **AuthCorsOptionsMiddleware** was added to handle OPTIONS for `/api/v1/auth/*` explicitly and always return 200 with correct CORS headers when origin is allowed.

---

## 3. Frontend (`web/`)

### 3.1 API client (`src/services/api.ts`)

- **Base URL:** `import.meta.env.VITE_API_BASE_URL || '/api/v1'` (relative in dev → Vite proxy).
- **Login:** `POST /auth/login` with `application/x-www-form-urlencoded` and `URLSearchParams` `username` / `password`.
- **Register:** `POST /auth/register` with JSON body (default `Content-Type`).
- **Interceptor:** Adds `Authorization: Bearer <token>` to **all** requests. That includes login/register when a stale token exists → preflight for those routes. We now **skip** adding `Authorization` for auth paths: `/auth/login`, `/auth/register`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/refresh`.

### 3.2 Vite proxy (`vite.config.ts`)

- **`/api`** → `process.env.VITE_API_BASE_URL || 'http://localhost:8000'`.
- Frontend calls `/api/v1/...`; proxy forwards to backend. Same-origin from the browser’s perspective, so no CORS for proxied requests. If `VITE_API_BASE_URL` is set to a full backend URL, the app may call the backend directly → cross-origin → preflight.

### 3.3 Login page (`src/pages/LoginPage.tsx`)

- Uses `validateUsernameOrEmail` and `validatePassword`. Submits trimmed `username` and `password` to `login()`.

### 3.4 Register page (`src/pages/RegisterPage.tsx`)

- Validates then submits trimmed `email`, `username`, `password`, `full_name` to `register()`. Uses `extractErrorMessage` for API errors.

### 3.5 Validation (`src/utils/validation.ts`)

- **validateUsernameOrEmail:** Accepts either username or email (if `@` present, validate as email).
- **validatePassword:** Min length 8, requires lower, upper, number, special.

---

## 4. Changes made

### 4.1 Backend

1. **Login**
   - Trim `username` and `password`.
   - Lookup by username, then by email.
   - Always log verify failure: `Login verify failed: user_id=... username=... hash_prefix=...` (plus existing DEBUG logs when `DEBUG=True`).

2. **Register**
   - Trim and normalize `username`, `email`, `password`; store normalized values.

3. **OPTIONS for auth**
   - New `AuthCorsOptionsMiddleware`: for `OPTIONS` to `/api/v1/auth/*`, return **200** with CORS headers (only when `Origin` is in `CORS_ORIGINS`). Ensures preflight never returns 400 for these paths.

### 4.2 Frontend

1. **API client**
   - Do **not** add `Authorization` for auth endpoints. Avoids preflight for login/register and prevents sending stale tokens.

2. **Login**
   - Trim username/password before validation and submit.
   - Label/placeholder: “Username or email”; use `validateUsernameOrEmail`.

3. **Register**
   - Trim email, username, password, full name; normalize email.
   - Use `extractErrorMessage` for API errors.

---

## 5. Recommendations

1. **Login 401**
   - Ensure `DEBUG=True` in `backend/.env` when debugging, then check logs for `Login verify` / `Login verify failed`.
   - Use a known password: e.g.  
     `python scripts/check_db_users.py --set-password elonmu 'TestPass123!'`  
     then log in with `elonmu` / `TestPass123!`.
   - Confirm no extra spaces or encoding issues (we now trim on both sides).

2. **OPTIONS 400**
   - Auth OPTIONS are now handled explicitly. If 400 persists, inspect middleware order and any reverse proxy in front of the app.

3. **Register “Email already registered”**
   - Use a unique email. The analyzer already checks both username and email.

4. **CORS**
   - When using the proxy, CORS usually doesn’t apply. When calling the backend directly (e.g. via `VITE_API_BASE_URL`), ensure the frontend origin is in `CORS_ORIGINS` and that OPTIONS are handled (as with the new middleware).

---

## 6. Quick reference

| Item | Location |
|------|----------|
| Login endpoint | `backend/app/api/v1/endpoints/auth.py` |
| Register endpoint | same |
| Auth OPTIONS middleware | `backend/app/middleware/cors_options.py` |
| API client / interceptors | `web/src/services/api.ts` |
| Login form | `web/src/pages/LoginPage.tsx` |
| Register form | `web/src/pages/RegisterPage.tsx` |
| DB/user check script | `backend/scripts/check_db_users.py` |
