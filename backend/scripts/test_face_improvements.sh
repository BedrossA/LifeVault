# Tests: Multiple encodings, multi-face detection, adaptive thresholds

set -e

echo "🧪 Testing Enhanced Face Recognition Features"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000/api/v1"
TOKEN=""  # Will be set after login

# ============================================
# HELPER FUNCTIONS
# ============================================

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ============================================
# 1. SETUP & AUTHENTICATION
# ============================================

if ! curl -s --head  --request GET http://localhost:8000/health | grep "200" > /dev/null; then
  print_error "Server is not running on localhost:8000"
  exit 1
fi

print_step "Step 1: Authentication"

# Login to get token
echo -n "Enter username: "
read USERNAME
echo -n "Enter password: "
read -s PASSWORD
echo ""

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    print_error "Login failed!"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

print_success "Logged in successfully"
echo ""

# ============================================
# 2. CHECK CURRENT STATUS
# ============================================

print_step "Step 2: Checking current face enrollment status"

STATS=$(curl -s -X GET "$BASE_URL/face/stats" \
  -H "Authorization: Bearer $TOKEN")

echo "$STATS" | jq '.'
echo ""

TOTAL_FACES=$(echo $STATS | jq -r '.total_faces')
print_success "You have $TOTAL_FACES face(s) enrolled"
echo ""

# ============================================
# 3. TEST: ENROLL PRIMARY FACE
# ============================================

print_step "Step 3: Testing primary face enrollment"

echo "Do you want to enroll a new primary face? (y/n)"
read -r ENROLL_NEW

if [ "$ENROLL_NEW" = "y" ]; then
    echo "Enter path to your photo (e.g., ~/photo.jpg):"
    read PHOTO_PATH
    
    if [ ! -f "$PHOTO_PATH" ]; then
        print_error "File not found: $PHOTO_PATH"
        exit 1
    fi
    
    ENROLL_RESPONSE=$(curl -s -X POST "$BASE_URL/face/enroll" \
      -H "Authorization: Bearer $TOKEN" \
      -F "label=primary" \
      -F "image=@$PHOTO_PATH")
    
    echo "$ENROLL_RESPONSE" | jq '.'
    
    FACE_ID=$(echo $ENROLL_RESPONSE | jq -r '.face_id')
    QUALITY=$(echo $ENROLL_RESPONSE | jq -r '.quality_score')
    THRESHOLD=$(echo $ENROLL_RESPONSE | jq -r '.custom_threshold')
    
    print_success "Face enrolled! ID: $FACE_ID"
    print_success "Quality score: $QUALITY"
    
    if [ "$THRESHOLD" != "null" ]; then
        print_success "Adaptive threshold: $THRESHOLD"
    fi
    
    echo ""
else
    # Get first face ID from existing faces
    FACES=$(curl -s -X GET "$BASE_URL/face/my-faces" \
      -H "Authorization: Bearer $TOKEN")
    
    FACE_ID=$(echo $FACES | jq -r '.[0].id')
    
    if [ "$FACE_ID" = "null" ]; then
        print_error "No faces enrolled. Please enroll a face first."
        exit 1
    fi
    
    print_success "Using existing face ID: $FACE_ID"
    echo ""
fi

# ============================================
# 4. TEST: ADD MULTIPLE ENCODINGS
# ============================================

print_step "Step 4: Testing multiple encodings per face"

echo "This tests the ability to add multiple photos of the same person."
echo "Add another encoding (different angle/lighting)? (y/n)"
read -r ADD_ENCODING

if [ "$ADD_ENCODING" = "y" ]; then
    echo "Enter path to another photo of the same person:"
    read PHOTO_PATH_2
    
    if [ ! -f "$PHOTO_PATH_2" ]; then
        print_error "File not found: $PHOTO_PATH_2"
    else
        ADD_RESPONSE=$(curl -s -X POST "$BASE_URL/face/$FACE_ID/add-encoding" \
          -H "Authorization: Bearer $TOKEN" \
          -F "image=@$PHOTO_PATH_2")
        
        echo "$ADD_RESPONSE" | jq '.'
        
        ENCODING_COUNT=$(echo $ADD_RESPONSE | jq -r '.encoding_count')
        AVG_QUALITY=$(echo $ADD_RESPONSE | jq -r '.average_quality')
        
        print_success "Encoding added! Total: $ENCODING_COUNT"
        print_success "Average quality: $AVG_QUALITY"
        
        echo ""
        echo "💡 Tip: Add 3-5 encodings from different angles/lighting for best results"
        echo ""
    fi
fi

# ============================================
# 5. TEST: SINGLE FACE RECOGNITION
# ============================================

print_step "Step 5: Testing single face recognition"

echo "Test face recognition? (y/n)"
read -r TEST_RECOG

if [ "$TEST_RECOG" = "y" ]; then
    echo "Enter path to test photo (should be same person):"
    read TEST_PHOTO
    
    if [ ! -f "$TEST_PHOTO" ]; then
        print_error "File not found: $TEST_PHOTO"
    else
        print_step "Running recognition..."
        
        RECOG_RESPONSE=$(curl -s -X POST "$BASE_URL/face/recognize" \
          -F "image=@$TEST_PHOTO")
        
        echo "$RECOG_RESPONSE" | jq '.'
        
        RECOGNIZED=$(echo $RECOG_RESPONSE | jq -r '.recognized')
        CONFIDENCE=$(echo $RECOG_RESPONSE | jq -r '.confidence // 0')
        USERNAME_DETECTED=$(echo $RECOG_RESPONSE | jq -r '.username // "unknown"')
        TIME_MS=$(echo $RECOG_RESPONSE | jq -r '.detection_time_ms')
        
        if [ "$RECOGNIZED" = "true" ]; then
            print_success "Recognized: $USERNAME_DETECTED"
            print_success "Confidence: $CONFIDENCE"
            print_success "Time: ${TIME_MS}ms"
        else
            print_warning "Not recognized"
        fi
        
        echo ""
    fi
fi

# ============================================
# 6. TEST: MULTI-FACE DETECTION
# ============================================

print_step "Step 6: Testing multi-face detection"

echo "Test multi-face detection? (requires photo with multiple people) (y/n)"
read -r TEST_MULTI

if [ "$TEST_MULTI" = "y" ]; then
    echo "Enter path to photo with multiple faces:"
    read MULTI_PHOTO
    
    if [ ! -f "$MULTI_PHOTO" ]; then
        print_error "File not found: $MULTI_PHOTO"
    else
        print_step "Running multi-face detection..."
        
        MULTI_RESPONSE=$(curl -s -X POST "$BASE_URL/face/recognize-multi" \
          -F "image=@$MULTI_PHOTO")
        
        echo "$MULTI_RESPONSE" | jq '.'
        
        NUM_FACES=$(echo $MULTI_RESPONSE | jq -r '.num_faces_detected')
        NUM_RECOGNIZED=$(echo $MULTI_RESPONSE | jq '[.faces[] | select(.is_known == true)] | length')
        TIME_MS=$(echo $MULTI_RESPONSE | jq -r '.detection_time_ms')
        
        print_success "Detected: $NUM_FACES face(s)"
        print_success "Recognized: $NUM_RECOGNIZED user(s)"
        print_success "Time: ${TIME_MS}ms"
        
        echo ""
        echo "Detected faces:"
        echo "$MULTI_RESPONSE" | jq -r '.faces[] | 
            "- \(if .is_known then "✓ \(.username) (confidence: \(.confidence))" 
             else "✗ Unknown (confidence: \(.confidence))" end)"'
        
        echo ""
    fi
fi

# ============================================
# 7. VIEW DETAILED STATS
# ============================================

print_step "Step 7: Viewing detailed statistics"

DETAILS=$(curl -s -X GET "$BASE_URL/face/$FACE_ID/details" \
  -H "Authorization: Bearer $TOKEN")

echo "$DETAILS" | jq '.'

ENCODING_COUNT=$(echo $DETAILS | jq -r '.encoding_count')
RECOG_COUNT=$(echo $DETAILS | jq -r '.recognition_count')
RECOMMENDATION=$(echo $DETAILS | jq -r '.recommendation')

print_success "Encodings: $ENCODING_COUNT"
print_success "Recognitions: $RECOG_COUNT"
echo ""
echo "💡 $RECOMMENDATION"
echo ""

# ============================================
# 8. FINAL STATS
# ============================================

print_step "Step 8: Final statistics"

FINAL_STATS=$(curl -s -X GET "$BASE_URL/face/stats" \
  -H "Authorization: Bearer $TOKEN")

echo "$FINAL_STATS" | jq '.'

TOTAL_ENCODINGS=$(echo $FINAL_STATS | jq -r '.total_encodings')
AVG_QUALITY=$(echo $FINAL_STATS | jq -r '.average_quality')
TOTAL_RECOG=$(echo $FINAL_STATS | jq -r '.total_recognitions')

echo ""
print_success "Test Complete!"
echo ""
echo "📊 Summary:"
echo "  • Total faces: $TOTAL_FACES"
echo "  • Total encodings: $TOTAL_ENCODINGS"
echo "  • Average quality: $AVG_QUALITY"
echo "  • Total recognitions: $TOTAL_RECOG"
echo ""
