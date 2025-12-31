#!/bin/bash
# Test script for all intelligence features

echo "🧪 Testing LifeVault Intelligence Features"
echo "=========================================="

# Set base URL
BASE_URL="${BASE_URL:-http://localhost:8000/api/v1}"
TOKEN="${TOKEN:-}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓${NC} (HTTP $http_code)"
        return 0
    else
        echo -e "${RED}✗${NC} (HTTP $http_code)"
        echo "Response: $body"
        return 1
    fi
}

# Check if token is provided
if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}Warning: No token provided. Set TOKEN environment variable.${NC}"
    echo "Example: TOKEN=your_token ./test_all_intelligence.sh"
    exit 1
fi

echo ""
echo "1. Testing Correlation Detection"
test_endpoint "Get Correlations" "GET" "/intelligence/correlations?metrics=sleep_hours,exercise_minutes"

echo ""
echo "2. Testing Anomaly Detection"
test_endpoint "Get Anomalies" "GET" "/intelligence/anomalies/sleep_hours?method=zscore"

echo ""
echo "3. Testing Pattern Recognition"
test_endpoint "Get Patterns" "GET" "/intelligence/patterns/sleep_hours"

echo ""
echo "4. Testing Predictive Analytics"
test_endpoint "Get Forecast" "GET" "/intelligence/forecast/sleep_hours?periods=7&method=linear"

echo ""
echo "5. Testing Recommendations"
test_endpoint "Get Recommendations" "GET" "/intelligence/recommendations"

echo ""
echo "6. Testing Activity Logging"
test_endpoint "Get Activities" "GET" "/intelligence/activities?limit=10"
test_endpoint "Get Activity Stats" "GET" "/intelligence/activities/stats?days=30"

echo ""
echo "7. Testing Goal Milestones"
# First create a goal (if you have goal_id)
# test_endpoint "Get Milestones" "GET" "/goals/{goal_id}/milestones"

echo ""
echo "=========================================="
echo -e "${GREEN}Testing Complete!${NC}"

