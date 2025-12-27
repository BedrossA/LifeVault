#!/bin/bash
# Comprehensive Feature Test Script
# Tests ALL LifeVault endpoints: Auth, Face, Analytics

set -e

BASE_URL="http://localhost:8000/api/v1"
TOKEN=""

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
# ============================================

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="${5:-200}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${BLUE}▶ Testing: $name${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
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
        echo "$body"
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

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

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

echo ""

# ============================================
# 2. SLEEP TRACKING TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}2️⃣  SLEEP TRACKING TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Create sleep log
TODAY=$(date +%Y-%m-%d)
test_endpoint "Create sleep log" "POST" "/analytics/sleep" \
    "{\"date\":\"$TODAY\",\"hours\":7.5,\"quality\":8,\"bedtime\":\"23:00\",\"waketime\":\"06:30\"}" \
    200

# List sleep logs
test_endpoint "List sleep logs" "GET" "/analytics/sleep"

# Get sleep stats
test_endpoint "Get sleep statistics" "GET" "/analytics/sleep/stats/summary?days=30"

echo ""

# ============================================
# 3. MOOD TRACKING TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}3️⃣  MOOD TRACKING TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Create mood log
test_endpoint "Create mood log" "POST" "/analytics/mood" \
    "{\"date\":\"$TODAY\",\"mood_score\":8,\"energy_level\":7,\"stress_level\":3,\"tags\":[\"productive\",\"happy\"]}"

# List mood logs
test_endpoint "List mood logs" "GET" "/analytics/mood"

echo ""

# ============================================
# 4. EXERCISE TRACKING TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}4️⃣  EXERCISE TRACKING TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Create exercise log
test_endpoint "Create exercise log" "POST" "/analytics/exercise" \
    "{\"date\":\"$TODAY\",\"activity_type\":\"running\",\"duration_minutes\":30,\"calories\":300,\"distance_km\":5.0,\"intensity\":\"moderate\"}"

# List exercise logs
test_endpoint "List exercise logs" "GET" "/analytics/exercise"

# Filter by activity type
test_endpoint "Filter by activity type" "GET" "/analytics/exercise?activity_type=running"

echo ""

# ============================================
# 5. NUTRITION TRACKING TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}5️⃣  NUTRITION TRACKING TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Create nutrition log
test_endpoint "Create nutrition log" "POST" "/analytics/nutrition" \
    "{\"date\":\"$TODAY\",\"meal_type\":\"breakfast\",\"description\":\"Eggs and toast\",\"calories\":450,\"protein_g\":25,\"carbs_g\":50,\"fat_g\":15}"

# List nutrition logs
test_endpoint "List nutrition logs" "GET" "/analytics/nutrition"

# Filter by meal type
test_endpoint "Filter by meal type" "GET" "/analytics/nutrition?meal_type=breakfast"

echo ""

# ============================================
# 6. WEIGHT TRACKING TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}6️⃣  WEIGHT TRACKING TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Create weight log
test_endpoint "Create weight log" "POST" "/analytics/weight" \
    "{\"date\":\"$TODAY\",\"weight_kg\":75.5,\"body_fat_percent\":18.5,\"muscle_mass_kg\":61.0}"

# List weight logs
test_endpoint "List weight logs" "GET" "/analytics/weight"

echo ""

# ============================================
# 7. FINANCE TRACKING TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}7️⃣  FINANCE TRACKING TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Create income log
test_endpoint "Create income log" "POST" "/analytics/finance" \
    "{\"date\":\"$TODAY\",\"transaction_type\":\"income\",\"amount\":3000,\"category\":\"salary\",\"description\":\"Monthly salary\"}"

# Create expense log
test_endpoint "Create expense log" "POST" "/analytics/finance" \
    "{\"date\":\"$TODAY\",\"transaction_type\":\"expense\",\"amount\":50,\"category\":\"food\",\"description\":\"Groceries\"}"

# List finance logs
test_endpoint "List finance logs" "GET" "/analytics/finance"

# Filter by type
test_endpoint "Filter by transaction type" "GET" "/analytics/finance?transaction_type=expense"

# Get finance stats
test_endpoint "Get finance statistics" "GET" "/analytics/finance/stats/summary?days=30"

echo ""

# ============================================
# 8. WATER TRACKING TESTS
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}8️⃣  WATER TRACKING TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Create water log
test_endpoint "Create water log" "POST" "/analytics/water" \
    "{\"date\":\"$TODAY\",\"amount_ml\":500,\"goal_ml\":2000}"

# Add more water (should accumulate)
test_endpoint "Add more water" "POST" "/analytics/water" \
    "{\"date\":\"$TODAY\",\"amount_ml\":300,\"goal_ml\":2000}"

# List water logs
test_endpoint "List water logs" "GET" "/analytics/water"

echo ""

# ============================================
# 9. DAILY SUMMARY TEST
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}9️⃣  DAILY SUMMARY TEST${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Get daily summary
test_endpoint "Get daily summary" "GET" "/analytics/summary/daily?target_date=$TODAY"

echo ""

# ============================================
# 10. FACE RECOGNITION TESTS (if images available)
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}🔟 FACE RECOGNITION TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# List enrolled faces
test_endpoint "List enrolled faces" "GET" "/face/my-faces"

# Get face stats
test_endpoint "Get face statistics" "GET" "/face/stats"

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
REPORT_FILE="/tmp/lifevault_test_report_$(date +%Y%m%d_%H%M%S).txt"
cat > "$REPORT_FILE" << REPORTEOF
LifeVault Test Report
=====================
Date: $(date)
User: $TEST_USERNAME

Results:
- Total Tests: $TOTAL_TESTS
- Passed: $PASSED_TESTS
- Failed: $FAILED_TESTS
- Success Rate: $SUCCESS_RATE%

Endpoints Tested:
✅ Authentication
✅ Sleep Tracking
✅ Mood Tracking
✅ Exercise Tracking
✅ Nutrition Tracking
✅ Weight Tracking
✅ Finance Tracking
✅ Water Tracking
✅ Daily Summary
✅ Face Recognition

Token Used: ${TOKEN:0:50}...
REPORTEOF

echo "📝 Test report saved to: $REPORT_FILE"
echo ""

exit $FAILED_TESTS
