echo "👤 LifeVault User Management Tool"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================
# 1. LIST ALL USERS
# ============================================

echo -e "${BLUE}📋 Current Users in Database${NC}"
echo "----------------------------"

python << 'PYEOF'
import sys
sys.path.append('/home/bpi/projects/LifeVault/backend')

from app.db.base import SessionLocal
from app.models.user import User
from datetime import datetime

db = SessionLocal()

try:
    users = db.query(User).all()
    
    if not users:
        print("❌ No users found in database")
    else:
        print(f"Found {len(users)} user(s):\n")
        
        for user in users:
            print(f"{'='*60}")
            print(f"👤 Username: {user.username}")
            print(f"📧 Email:    {user.email}")
            print(f"🆔 User ID:  {user.id}")
            print(f"✅ Active:   {user.is_active}")
            print(f"📅 Created:  {user.created_at}")
            print(f"{'='*60}")
            print()
            
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
PYEOF

echo ""

# ============================================
# 2. GET USER CREDENTIALS
# ============================================

echo -e "${BLUE}🔑 User Credentials (for testing)${NC}"
echo "-----------------------------------"
echo ""

python << 'PYEOF'
import sys
sys.path.append('/home/bpi/projects/LifeVault/backend')

from app.db.base import SessionLocal
from app.models.user import User

db = SessionLocal()

try:
    users = db.query(User).all()
    
    if users:
        print("⚠️  Note: Passwords are hashed. Original passwords:")
        print()
        
        # Common test passwords (you should know these from creation)
        print("If you used standard registration, likely passwords are:")
        print("  - Password123!")
        print("  - TestPassword123")
        print("  - Admin123!")
        print()
        
        print("Users available for login:")
        for user in users:
            print(f"  Username: {user.username}")
            print(f"  Email:    {user.email}")
            print()
            
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
PYEOF

echo ""

# ============================================
# 3. GENERATE ACCESS TOKEN
# ============================================

echo -e "${BLUE}🎫 Generate Access Token${NC}"
echo "-------------------------"
echo ""

read -p "Enter username to generate token: " USERNAME
read -sp "Enter password: " PASSWORD
echo ""
echo ""

echo "Generating token..."

TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD")

TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}❌ Login failed${NC}"
    echo "Response: $TOKEN_RESPONSE"
else
    echo -e "${GREEN}✅ Token generated successfully!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}ACCESS TOKEN:${NC}"
    echo "$TOKEN"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Save to file
    echo "$TOKEN" > /tmp/lifevault_token.txt
    echo "💾 Token saved to: /tmp/lifevault_token.txt"
    echo ""
    
    # Export as environment variable
    export LIFEVAULT_TOKEN=$TOKEN
    echo "🔐 Token exported as: \$LIFEVAULT_TOKEN"
    echo ""
    
    echo "📝 Usage Examples:"
    echo ""
    echo "# Using saved token file:"
    echo 'TOKEN=$(cat /tmp/lifevault_token.txt)'
    echo 'curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/analytics/sleep'
    echo ""
    echo "# Using environment variable:"
    echo 'curl -H "Authorization: Bearer $LIFEVAULT_TOKEN" http://localhost:8000/api/v1/analytics/sleep'
    echo ""
    
    # Decode token to show expiry
    echo "🔍 Token Details:"
    python << PYEOF
import jwt
import json
from datetime import datetime

token = "$TOKEN"
try:
    # Decode without verification (just to see contents)
    decoded = jwt.decode(token, options={"verify_signature": False})
    print(f"  User ID: {decoded.get('sub')}")
    
    exp = decoded.get('exp')
    if exp:
        exp_time = datetime.fromtimestamp(exp)
        print(f"  Expires: {exp_time}")
        
        remaining = exp_time - datetime.now()
        if remaining.total_seconds() > 0:
            hours = remaining.total_seconds() / 3600
            print(f"  Valid for: {hours:.1f} hours")
        else:
            print("  ⚠️  Token expired!")
except Exception as e:
    print(f"  Could not decode: {e}")
PYEOF
    
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ============================================
# 4. CREATE NEW TEST USER
# ============================================

echo ""
echo -e "${BLUE}➕ Create New Test User${NC}"
echo "------------------------"
echo ""

read -p "Create a new test user? (y/n): " CREATE_USER

if [ "$CREATE_USER" = "y" ]; then
    read -p "Username: " NEW_USERNAME
    read -p "Email: " NEW_EMAIL
    read -sp "Password: " NEW_PASSWORD
    echo ""
    
    CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
      -H "Content-Type: application/json" \
      -d "{\"username\":\"$NEW_USERNAME\",\"email\":\"$NEW_EMAIL\",\"password\":\"$NEW_PASSWORD\"}")
    
    USER_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
    
    if [ "$USER_ID" = "null" ] || [ -z "$USER_ID" ]; then
        echo -e "${YELLOW}❌ Registration failed${NC}"
        echo "Response: $CREATE_RESPONSE"
    else
        echo -e "${GREEN}✅ User created successfully!${NC}"
        echo ""
        echo "User Details:"
        echo "  Username: $NEW_USERNAME"
        echo "  Email:    $NEW_EMAIL"
        echo "  Password: $NEW_PASSWORD"
        echo "  User ID:  $USER_ID"
        echo ""
        echo "💾 Saved credentials to: /tmp/lifevault_test_user.txt"
        
        cat > /tmp/lifevault_test_user.txt << USEREOF
LifeVault Test User Credentials
================================
Username: $NEW_USERNAME
Email:    $NEW_EMAIL  
Password: $NEW_PASSWORD
User ID:  $USER_ID
Created:  $(date)
USEREOF
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ============================================
# 5. USER SUMMARY
# ============================================

echo ""
echo -e "${BLUE}📊 Quick Summary${NC}"
echo "-----------------"
echo ""

python << 'PYEOF'
import sys
sys.path.append('/home/bpi/projects/LifeVault/backend')

from app.db.base import SessionLocal
from app.models.user import User
from app.models.face import Face
from app.models.analytics import SleepLog, MoodLog, ExerciseLog, FinanceLog

db = SessionLocal()

try:
    users = db.query(User).all()
    print(f"Total Users: {len(users)}")
    
    for user in users:
        faces = db.query(Face).filter(Face.user_id == user.id).count()
        sleep = db.query(SleepLog).filter(SleepLog.user_id == user.id).count()
        mood = db.query(MoodLog).filter(MoodLog.user_id == user.id).count()
        exercise = db.query(ExerciseLog).filter(ExerciseLog.user_id == user.id).count()
        finance = db.query(FinanceLog).filter(FinanceLog.user_id == user.id).count()
        
        print(f"\n  {user.username}:")
        print(f"    Faces: {faces}")
        print(f"    Sleep logs: {sleep}")
        print(f"    Mood logs: {mood}")
        print(f"    Exercise logs: {exercise}")
        print(f"    Finance logs: {finance}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
PYEOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Quick Actions:"
echo ""
echo "  1. View this info again:"
echo "     bash scripts/user_management.sh"
echo ""
echo "  2. Get token for user:"
echo "     TOKEN=\$(bash scripts/get_token.sh USERNAME PASSWORD)"
echo ""
echo "  3. Test all endpoints:"
echo "     bash scripts/test_all_features.sh"
echo ""
echo "  4. View saved credentials:"
echo "     cat /tmp/lifevault_test_user.txt"
echo ""
