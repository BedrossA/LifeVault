#!/usr/bin/env python3
"""
Diagnostic script: verify PostgreSQL connection, list usernames, optionally test login.
Usage:
  python scripts/check_db_users.py
  python scripts/check_db_users.py <username> [password]
  python scripts/check_db_users.py --set-password <username> <new_password>
"""
import sys
import os

# Ensure backend root is on path and cwd for .env
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(backend_root)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

def set_password(username: str, new_password: str) -> int:
    """Set a new password for username. Returns 0 on success, 1 on error."""
    from app.db.base import SessionLocal
    from app.models.user import User
    from app.core import security

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User {username!r} not found.")
            return 1
        user.hashed_password = security.get_password_hash(new_password)
        user.failed_login_attempts = 0
        db.commit()
        print(f"Password updated for {username!r}. You can now log in with the new password.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        return 1
    finally:
        db.close()

def main():
    from app.core.config import settings
    from app.db.base import engine, SessionLocal
    from app.models.user import User
    from app.core import security
    from sqlalchemy import text

    # Mask DATABASE_URL for safe printing (hide password)
    url = settings.DATABASE_URL
    if "@" in url and "//" in url:
        pre, rest = url.split("//", 1)
        if "@" in rest:
            creds, host_db = rest.split("@", 1)
            if ":" in creds:
                user_part = creds.split(":")[0]
                masked = f"{pre}//{user_part}:****@{host_db}"
            else:
                masked = f"{pre}//****@{host_db}"
        else:
            masked = f"{pre}//****"
    else:
        masked = "****"

    print("=" * 60)
    print("LifeVault DB & users check")
    print("=" * 60)
    print(f"DATABASE_URL: {masked}")
    print()

    # 1. Test raw connection
    print("1. Testing PostgreSQL connection...")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("   OK – PostgreSQL is reachable.")
    except Exception as e:
        print(f"   FAIL – Cannot connect: {e}")
        return 1

    # 2. Check users table exists
    print("\n2. Checking 'users' table...")
    try:
        with engine.connect() as conn:
            r = conn.execute(text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = 'users')"
            ))
            exists = r.scalar()
        if exists:
            print("   OK – 'users' table exists.")
        else:
            print("   FAIL – 'users' table not found. Run migrations or init_db.")
            return 1
    except Exception as e:
        print(f"   FAIL – {e}")
        return 1

    # 3. List usernames
    print("\n3. Usernames in database:")
    print("-" * 40)
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("   (none)")
        else:
            for u in users:
                print(f"   username: {u.username!r}  email: {u.email!r}  active={u.is_active}")
        print("-" * 40)
        print(f"   Total: {len(users)} user(s)")
    except Exception as e:
        print(f"   FAIL – {e}")
        return 1
    finally:
        db.close()

    # 4. Optional: --set-password <username> <new_password>
    argv = sys.argv[1:]
    if len(argv) >= 3 and argv[0] == "--set-password":
        return set_password(argv[1].strip(), argv[2])

    # 5. Optional: check specific user / password
    if len(argv) >= 1:
        username = argv[0].strip()
        password = argv[1] if len(argv) >= 2 else ""
        print(f"\n4. Checking user {username!r}...")
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                print(f"   User {username!r} NOT FOUND.")
                return 0
            print(f"   User exists: id={user.id}, email={user.email}, active={user.is_active}")
            if password:
                ok = security.verify_password(password, user.hashed_password)
                if ok:
                    print("   Password: OK – matches.")
                else:
                    print("   Password: INCORRECT – does not match stored hash.")
            else:
                print("   (No password provided; use: python check_db_users.py <username> <password>)")
        finally:
            db.close()
    else:
        print("\n4. Tip: run with 'python scripts/check_db_users.py <username> [password]' to verify login.")
        print("    Reset password: 'python scripts/check_db_users.py --set-password <username> <new_password>'")

    print("\n" + "=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
