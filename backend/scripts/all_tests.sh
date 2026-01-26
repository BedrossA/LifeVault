#!/bin/bash
# Automated LifeVault Feature Test Runner
# Tests all features and generates a comprehensive report

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
OUTPUT_DIR="./test_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$OUTPUT_DIR/test_report_$TIMESTAMP.txt"

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "🧪 LifeVault Automated Test Suite" | tee "$REPORT_FILE"
echo "=================================" | tee -a "$REPORT_FILE"
echo "Started: $(date)" | tee -a "$REPORT_FILE"
echo "Base URL: $BASE_URL" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Function to test an endpoint
test_endpoint() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="${5:-200}"
    local token="$6"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Testing: $test_name... " | tee -a "$REPORT_FILE"
    
    # Build curl command
    local curl_cmd="curl -s -w '\n%{http_code}' -X $method '$BASE_URL$endpoint'"
    
    if [ -n "$token" ]; then
        curl_cmd="$curl_cmd -H 'Authorization: Bearer $token'"
    fi
    
    if [ -n "$data" ]; then
        curl_cmd="$curl_cmd -H 'Content-Type: application/json' -d '$data'"
    fi
    
    # Execute request
    local response
    response=$(eval "$curl_cmd" 2>&1)
    
    local status_code
    status_code=$(echo "$response" | tail -n1)
    
    local body
    body=$(echo "$response" | head -n-1)
    
    # Check result
    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}PASS${NC} (HTTP $status_code)" | tee -a "$REPORT_FILE"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} (Expected: $expected_status, Got: $status_code)" | tee -a "$REPORT_FILE"
        echo "  Response: $body" >> "$REPORT_FILE"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Check if server is running
echo -e "${BLUE}Checking server availability...${NC}" | tee -a "$REPORT_FILE"
if ! curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Server is not running at $BASE_URL${NC}" | tee -a "$REPORT_FILE"
    echo "Please start the server and try again." | tee -a "$REPORT_FILE"
    exit 1
fi
echo -e "${GREEN}✓ Server is running${NC}" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Test 1: Health Check
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}Test Suite 1: System Health${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"
test_endpoint "Health Check" "GET" "/health" "" 200
test_endpoint "Root Endpoint" "GET" "/" "" 200
echo "" | tee -a "$REPORT_FILE"

# Test 2: Authentication
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}Test Suite 2: Authentication${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"

# Generate random test user
TEST_USER="testuser_$RANDOM"
TEST_EMAIL="$TEST_USER@example.com"
TEST_PASSWORD="SecureP@ssw0rd123"

# Register
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$TEST_USER\",\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

if echo "$REGISTER_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC} Registration" | tee -a "$REPORT_FILE"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${RED}FAIL${NC} Registration" | tee -a "$REPORT_FILE"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# Login
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$TEST_USER&password=$TEST_PASSWORD")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo -e "${GREEN}PASS${NC} Login" | tee -a "$REPORT_FILE"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${RED}FAIL${NC} Login" | tee -a "$REPORT_FILE"
    echo "Cannot proceed with authenticated tests" | tee -a "$REPORT_FILE"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    exit 1
fi

test_endpoint "Get Current User" "GET" "/api/v1/auth/me" "" 200 "$TOKEN"
test_endpoint "Get Login History" "GET" "/api/v1/auth/history" "" 200 "$TOKEN"
echo "" | tee -a "$REPORT_FILE"

# Test 3: Analytics
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}Test Suite 3: Analytics${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"

# Create entries
ENTRY_DATA='{"category":"health","metric":"steps","value":10000,"unit":"steps"}'
CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/analytics/entries" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$ENTRY_DATA")

STATUS=$(echo "$CREATE_RESPONSE" | tail -n1)
BODY=$(echo "$CREATE_RESPONSE" | head -n-1)
ENTRY_ID=$(echo "$BODY" | jq -r '.id // empty')

if [ "$STATUS" -eq 201 ] && [ -n "$ENTRY_ID" ]; then
    echo -e "${GREEN}PASS${NC} Create Analytics Entry" | tee -a "$REPORT_FILE"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}FAIL${NC} Create Analytics Entry" | tee -a "$REPORT_FILE"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

test_endpoint "List Entries" "GET" "/api/v1/analytics/entries" "" 200 "$TOKEN"
test_endpoint "Get Statistics" "GET" "/api/v1/analytics/stats" "" 200 "$TOKEN"

if [ -n "$ENTRY_ID" ]; then
    test_endpoint "Get Single Entry" "GET" "/api/v1/analytics/entries/$ENTRY_ID" "" 200 "$TOKEN"
fi

echo "" | tee -a "$REPORT_FILE"

# Test 4: Goals
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}Test Suite 4: Goals${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"

GOAL_DATA='{"metric":"steps","category":"health","target_value":10000}'
test_endpoint "Create Goal" "POST" "/api/v1/analytics/goals" "$GOAL_DATA" 201 "$TOKEN"
test_endpoint "List Goals" "GET" "/api/v1/analytics/goals" "" 200 "$TOKEN"
echo "" | tee -a "$REPORT_FILE"

# Test 5: Intelligence Features
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}Test Suite 5: Intelligence${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"

# Create sample data for intelligence tests
for i in {1..5}; do
    curl -s -X POST "$BASE_URL/api/v1/analytics/entries" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"category\":\"health\",\"metric\":\"sleep_hours\",\"value\":$((7 + i))}" > /dev/null
done

test_endpoint "Get Recommendations" "GET" "/api/v1/intelligence/recommendations" "" 200 "$TOKEN"
test_endpoint "Get Activities" "GET" "/api/v1/intelligence/activities?limit=10" "" 200 "$TOKEN"
test_endpoint "Get Activity Stats" "GET" "/api/v1/intelligence/activities/stats" "" 200 "$TOKEN"
echo "" | tee -a "$REPORT_FILE"

# Test 6: Face Recognition
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}Test Suite 6: Face Recognition${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"

test_endpoint "List Enrolled Faces" "GET" "/api/v1/face/my-faces" "" 200 "$TOKEN"
test_endpoint "Get Face Stats" "GET" "/api/v1/face/stats" "" 200 "$TOKEN"
test_endpoint "Get Face Config" "GET" "/api/v1/face/config" "" 200 "$TOKEN"
echo "" | tee -a "$REPORT_FILE"

# Test 7: Error Handling
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}Test Suite 7: Error Handling${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"

test_endpoint "Unauthorized Access" "GET" "/api/v1/auth/me" "" 401
test_endpoint "Invalid Entry ID" "GET" "/api/v1/analytics/entries/invalid_id" "" 400 "$TOKEN"
test_endpoint "Not Found" "GET" "/api/v1/analytics/entries/507f1f77bcf86cd799439011" "" 404 "$TOKEN"
echo "" | tee -a "$REPORT_FILE"

# Test 8: Input Validation
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}Test Suite 8: Input Validation${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}═══════════════════════════════════${NC}" | tee -a "$REPORT_FILE"

test_endpoint "Missing Fields" "POST" "/api/v1/analytics/entries" '{"category":"test"}' 422 "$TOKEN"
test_endpoint "Invalid Email" "POST" "/api/v1/auth/register" '{"username":"test","email":"invalid","password":"Pass123!"}' 422
echo "" | tee -a "$REPORT_FILE"

# Generate Summary
echo "" | tee -a "$REPORT_FILE"
echo "═════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo -e "${BLUE}TEST RESULTS SUMMARY${NC}" | tee -a "$REPORT_FILE"
echo "═════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"
echo "Total Tests:    $TOTAL_TESTS" | tee -a "$REPORT_FILE"
echo -e "${GREEN}Passed:         $PASSED_TESTS ✓${NC}" | tee -a "$REPORT_FILE"
echo -e "${RED}Failed:         $FAILED_TESTS ✗${NC}" | tee -a "$REPORT_FILE"
echo -e "${YELLOW}Skipped:        $SKIPPED_TESTS ⊘${NC}" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo "Success Rate:   $SUCCESS_RATE%" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}" | tee -a "$REPORT_FILE"
else
    echo -e "${YELLOW}⚠️  Some tests failed. Check the report for details.${NC}" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"
echo "Completed: $(date)" | tee -a "$REPORT_FILE"
echo "Report saved to: $REPORT_FILE" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Create summary JSON
cat > "$OUTPUT_DIR/test_summary_$TIMESTAMP.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "base_url": "$BASE_URL",
  "total_tests": $TOTAL_TESTS,
  "passed": $PASSED_TESTS,
  "failed": $FAILED_TESTS,
  "skipped": $SKIPPED_TESTS,
  "success_rate": $SUCCESS_RATE,
  "test_user": "$TEST_USER"
}
EOF

echo "JSON summary saved to: $OUTPUT_DIR/test_summary_$TIMESTAMP.json"

exit $FAILED_TESTS