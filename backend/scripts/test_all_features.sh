#!/bin/bash
# Comprehensive Feature Test Script
# Tests ALL LifeVault endpoints: Auth, Analytics, Face Recognition

set -e

BASE_URL="http://192.168.0.109:8000/api/v1"
TOKEN=""
REFRESH_TOKEN=""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ============================================
# Helper Functions
# ===========================================

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="${5:-200}"
    local content_type="${6:-application/json}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${BLUE}▶ Testing: $name${NC}"
    
    if [ "$method" = "GET" ]; then
        if [ -z "$TOKEN" ]; then
            response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" \
                -H "Authorization: Bearer $TOKEN")
        fi
    elif [ "$method" = "POST" ]; then
        if [ "$content_type" = "application/x-www-form-urlencoded" ]; then
            if [ -z "$TOKEN" ]; then
                response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
                    -H "Content-Type: $content_type" \
                    -d "$data")
            else
                response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
                    -H "Authorization: Bearer $TOKEN" \
                    -H "Content-Type: $content_type" \
                    -d "$data")
            fi
        else
            if [ -z "$TOKEN" ]; then
                response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
                    -H "Content-Type: $content_type" \
                    -d "$data")
            else
                response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
                    -H "Authorization: Bearer $TOKEN" \
                    -H "Content-Type: $content_type" \
                    -d "$data")
            fi
        fi
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: $content_type" \
            -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (Status: $status_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    fi
    
    echo ""
}

# ============================================
# Main Test Flow
# ============================================

echo "🧪 LifeVault Comprehensive Feature Test"
echo "========================================"
echo ""

# ============================================
# 1. AUTHENTICATION TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}1️⃣  AUTHENTICATION TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Get credentials
echo "Enter test credentials:"
read -p "Username: " TEST_USERNAME
read -sp "Password: " TEST_PASSWORD
echo ""
echo ""

# Login
echo "🔐 Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$TEST_USERNAME&password=$TEST_PASSWORD")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token // empty')
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.refresh_token // empty')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Login failed!${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Login successful!${NC}"
echo "Token: ${TOKEN:0:50}..."
echo ""

PASSED_TESTS=$((PASSED_TESTS + 1))
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Get current user
test_endpoint "Get current user" "GET" "/auth/me"

# Get login history
test_endpoint "Get login history" "GET" "/auth/history?limit=5"

# Get user activity
test_endpoint "Get user activity" "GET" "/auth/activity?limit=5"

# Test token refresh
if [ -n "$REFRESH_TOKEN" ] && [ "$REFRESH_TOKEN" != "null" ]; then
    test_endpoint "Refresh token" "POST" "/auth/refresh" \
        "{\"refresh_token\":\"$REFRESH_TOKEN\"}"
    
    # Update TOKEN with new one
    REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/refresh" \
        -H "Content-Type: application/json" \
        -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}")
    NEW_TOKEN=$(echo $REFRESH_RESPONSE | jq -r '.access_token // empty' 2>/dev/null || echo "")
    if [ -n "$NEW_TOKEN" ] && [ "$NEW_TOKEN" != "null" ]; then
        TOKEN="$NEW_TOKEN"
    fi
fi

echo ""

# ============================================
# 2. ANALYTICS ENTRIES TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}2️⃣  ANALYTICS ENTRIES TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

TODAY=$(date +%Y-%m-%d)
ENTRY_ID=""

# Create analytics entry - Health (and capture ID)
echo -e "${BLUE}▶ Testing: Create health entry (steps)${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
ENTRY_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/analytics/entries" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"category\":\"health\",\"metric\":\"steps\",\"value\":8500,\"unit\":\"steps\",\"notes\":\"Morning walk\"}")

STATUS_CODE=$(echo "$ENTRY_RESPONSE" | tail -n1)
BODY=$(echo "$ENTRY_RESPONSE" | head -n-1)

if [ "$STATUS_CODE" -eq 201 ]; then
    echo -e "${GREEN}✅ PASS${NC} (Status: $STATUS_CODE)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    ENTRY_ID=$(echo "$BODY" | jq -r '.id // empty' 2>/dev/null || echo "")
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}❌ FAIL${NC} (Expected: 201, Got: $STATUS_CODE)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo "$BODY"
    ENTRY_ID=""
fi
echo ""

# Create more entries
test_endpoint "Create fitness entry (calories)" "POST" "/analytics/entries" \
    "{\"category\":\"fitness\",\"metric\":\"calories\",\"value\":450,\"unit\":\"kcal\",\"notes\":\"Running session\"}" \
    201

test_endpoint "Create productivity entry (hours)" "POST" "/analytics/entries" \
    "{\"category\":\"productivity\",\"metric\":\"hours\",\"value\":8.5,\"unit\":\"hours\",\"notes\":\"Work day\"}" \
    201

test_endpoint "Create mood entry" "POST" "/analytics/entries" \
    "{\"category\":\"mood\",\"metric\":\"mood_score\",\"value\":7.5,\"unit\":\"out of 10\",\"notes\":\"Feeling good\"}" \
    201

# List all entries
test_endpoint "List all entries" "GET" "/analytics/entries"

# List entries by category
test_endpoint "List entries by category (health)" "GET" "/analytics/entries?category=health"

# List entries with date range
test_endpoint "List entries with date range" "GET" "/analytics/entries?start_date=$TODAY&end_date=$TODAY"

# Get single entry (if we have an ID)
if [ -n "$ENTRY_ID" ] && [ "$ENTRY_ID" != "null" ]; then
    test_endpoint "Get single entry" "GET" "/analytics/entries/$ENTRY_ID"
    
    # Update entry
    test_endpoint "Update entry" "PUT" "/analytics/entries/$ENTRY_ID" \
        "{\"category\":\"fitness\",\"metric\":\"calories\",\"value\":500,\"unit\":\"kcal\",\"notes\":\"Updated running session\"}"
fi

echo ""

# ============================================
# 3. ANALYTICS STATISTICS TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}3️⃣  ANALYTICS STATISTICS TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Get statistics
test_endpoint "Get analytics statistics" "GET" "/analytics/stats"

# Get statistics with date range
test_endpoint "Get statistics with date range" "GET" "/analytics/stats?start_date=$TODAY&end_date=$TODAY"

# Get time series data
test_endpoint "Get time series (steps)" "GET" "/analytics/time-series?metric=steps"

test_endpoint "Get time series (calories)" "GET" "/analytics/time-series?metric=calories&category=fitness"

echo ""

# ============================================
# 4. GOALS TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}4️⃣  GOALS TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

GOAL_ID=""

# Create goal (and capture ID)
echo -e "${BLUE}▶ Testing: Create goal (steps)${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
GOAL_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/analytics/goals" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"metric\":\"steps\",\"category\":\"health\",\"target_value\":10000,\"unit\":\"steps\"}")

STATUS_CODE=$(echo "$GOAL_RESPONSE" | tail -n1)
BODY=$(echo "$GOAL_RESPONSE" | head -n-1)

if [ "$STATUS_CODE" -eq 201 ]; then
    echo -e "${GREEN}✅ PASS${NC} (Status: $STATUS_CODE)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    GOAL_ID=$(echo "$BODY" | jq -r '.id // empty' 2>/dev/null || echo "")
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}❌ FAIL${NC} (Expected: 201, Got: $STATUS_CODE)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo "$BODY"
    GOAL_ID=""
fi
echo ""

# Create another goal
test_endpoint "Create goal (calories)" "POST" "/analytics/goals" \
    "{\"metric\":\"calories\",\"category\":\"fitness\",\"target_value\":2000,\"unit\":\"kcal\"}" \
    201

# List goals
test_endpoint "List all goals" "GET" "/analytics/goals"

# Update goal (if we have an ID)
if [ -n "$GOAL_ID" ] && [ "$GOAL_ID" != "null" ]; then
    test_endpoint "Update goal" "PUT" "/analytics/goals/$GOAL_ID" \
        "{\"metric\":\"calories\",\"category\":\"fitness\",\"target_value\":2500,\"unit\":\"kcal\"}"
fi

echo ""

# ============================================
# 5. EXPORT TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}5️⃣  EXPORT TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Export JSON
echo -e "${BLUE}▶ Testing: Export data (JSON)${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
EXPORT_JSON=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/analytics/export?format=json" \
    -H "Authorization: Bearer $TOKEN")
STATUS_CODE=$(echo "$EXPORT_JSON" | tail -n1)
if [ "$STATUS_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ PASS${NC} (Status: $STATUS_CODE)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo "JSON export successful"
else
    echo -e "${RED}❌ FAIL${NC} (Status: $STATUS_CODE)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# Export CSV
echo -e "${BLUE}▶ Testing: Export data (CSV)${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
EXPORT_CSV=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/analytics/export?format=csv" \
    -H "Authorization: Bearer $TOKEN")
STATUS_CODE=$(echo "$EXPORT_CSV" | tail -n1)
if [ "$STATUS_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ PASS${NC} (Status: $STATUS_CODE)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo "CSV export successful"
else
    echo -e "${RED}❌ FAIL${NC} (Status: $STATUS_CODE)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# ============================================
# 6. FACE RECOGNITION TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}6️⃣  FACE RECOGNITION TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# List enrolled faces
test_endpoint "List enrolled faces" "GET" "/face/my-faces"

# Get face statistics
test_endpoint "Get face statistics" "GET" "/face/stats"

# Get face config
test_endpoint "Get face recognition config" "GET" "/face/config"

echo ""

# ============================================
# 7. CLEANUP (Optional)
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}7️⃣  CLEANUP (Optional)${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

read -p "Delete test entries and goals? (y/N): " CLEANUP
if [ "$CLEANUP" = "y" ] || [ "$CLEANUP" = "Y" ]; then
    if [ -n "$ENTRY_ID" ] && [ "$ENTRY_ID" != "null" ]; then
        test_endpoint "Delete test entry" "DELETE" "/analytics/entries/$ENTRY_ID" "" 204
    fi
    
    if [ -n "$GOAL_ID" ] && [ "$GOAL_ID" != "null" ]; then
        test_endpoint "Delete test goal" "DELETE" "/analytics/goals/$GOAL_ID" "" 204
    fi
fi

echo ""

# ============================================
# 8. LOGOUT TEST
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}8️⃣  LOGOUT TEST${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

test_endpoint "Logout" "POST" "/auth/logout" "" 200

echo ""

# ============================================
# FINAL RESULTS
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 TEST RESULTS SUMMARY${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total Tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed:       $PASSED_TESTS ✅${NC}"
echo -e "${RED}Failed:       $FAILED_TESTS ❌${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}"
    SUCCESS_RATE=100
else
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
fi

echo ""
echo "Success Rate: $SUCCESS_RATE%"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save test report
if [ -d "/tmp" ]; then
    REPORT_FILE="/tmp/lifevault_test_report_$(date +%Y%m%d_%H%M%S).txt"
elif [ -d "$TMPDIR" ]; then
    REPORT_FILE="$TMPDIR/lifevault_test_report_$(date +%Y%m%d_%H%M%S).txt"
else
    REPORT_FILE="./lifevault_test_report_$(date +%Y%m%d_%H%M%S).txt"
fi
cat > "$REPORT_FILE" << REPORTEOF
LifeVault Test Report
=====================
Date: $(date)
User: $TEST_USERNAME
Base URL: $BASE_URL

Results:
- Total Tests: $TOTAL_TESTS
- Passed: $PASSED_TESTS
- Failed: $FAILED_TESTS
- Success Rate: $SUCCESS_RATE%

Endpoints Tested:
✅ Authentication (Login, Me, History, Activity, Refresh, Logout)
✅ Analytics Entries (Create, List, Get, Update, Delete)
✅ Analytics Statistics (Stats, Time Series)
✅ Goals (Create, List, Update, Delete)
✅ Export (JSON, CSV)
✅ Face Recognition (List Faces, Stats, Config)

Token Used: ${TOKEN:0:50}...
REPORTEOF

echo "📝 Test report saved to: $REPORT_FILE"
echo ""

exit $FAILED_TESTS
