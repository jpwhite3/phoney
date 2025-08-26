#!/bin/bash
# Example: Using Phoney with curl for quick testing
# Make this executable: chmod +x examples/curl_examples.sh
# Run: ./examples/curl_examples.sh

# Configuration
PHONEY_URL="http://localhost:8000"

echo "🚀 Phoney API Examples with curl"
echo "=================================="
echo "Make sure Phoney server is running at $PHONEY_URL"
echo ""

# Function to make API calls and format output
call_api() {
    local endpoint="$1"
    local description="$2"
    
    echo "📋 $description"
    echo "   curl \"$PHONEY_URL$endpoint\""
    echo "   Response:"
    
    # Make the API call and format JSON output
    if command -v jq >/dev/null 2>&1; then
        curl -s "$PHONEY_URL$endpoint" | jq '.'
    else
        curl -s "$PHONEY_URL$endpoint"
    fi
    echo ""
}

# Basic Examples
echo "=== Basic Data Generation ==="
call_api "/fake/name" "Generate a random name"
call_api "/fake/email" "Generate an email address"
call_api "/fake/phone" "Generate a phone number"
call_api "/fake/address" "Generate a street address"
call_api "/fake/company" "Generate a company name"

# Multiple Items
echo "=== Multiple Items ==="
call_api "/fake/name?count=5" "Generate 5 names"
call_api "/fake/email?count=3" "Generate 3 email addresses"

# Localized Data
echo "=== Localized Data ==="
call_api "/fake/name?locale=fr_FR" "Generate French name"
call_api "/fake/address?locale=de_DE" "Generate German address"
call_api "/fake/name?locale=ja_JP" "Generate Japanese name"

# Reproducible Data (Seeds)
echo "=== Reproducible Data ==="
call_api "/fake/name?seed=42" "Generate name with seed 42 (try multiple times!)"
call_api "/fake/email?seed=123&count=3" "Generate 3 emails with seed 123"

# Different Data Types
echo "=== Different Data Types ==="
call_api "/fake/job" "Generate job title"
call_api "/fake/date" "Generate date"
call_api "/fake/url" "Generate URL"
call_api "/fake/text" "Generate text paragraph"
call_api "/fake/uuid4" "Generate UUID"
call_api "/fake/credit_card_number" "Generate credit card number (fake!)"

# Discovery
echo "=== Discovery ==="
echo "📋 List first 10 available generators"
echo "   curl \"$PHONEY_URL/generators\""
echo "   Response (first 10):"
if command -v jq >/dev/null 2>&1; then
    curl -s "$PHONEY_URL/generators" | jq '.[0:10]'
else
    curl -s "$PHONEY_URL/generators"
fi
echo ""

# Advanced Examples
echo "=== Advanced Examples ==="

# E-commerce user data
echo "📋 Generate complete user profile for e-commerce testing"
echo "   Creating user with name, email, phone, address..."

NAME=$(curl -s "$PHONEY_URL/fake/name" | jq -r '.data // .')
EMAIL=$(curl -s "$PHONEY_URL/fake/email" | jq -r '.data // .')
PHONE=$(curl -s "$PHONEY_URL/fake/phone" | jq -r '.data // .')
ADDRESS=$(curl -s "$PHONEY_URL/fake/address" | jq -r '.data // .')

if command -v jq >/dev/null 2>&1; then
    echo "   {"
    echo "     \"name\": \"$NAME\","
    echo "     \"email\": \"$EMAIL\","
    echo "     \"phone\": \"$PHONE\","
    echo "     \"address\": \"$ADDRESS\""
    echo "   }"
else
    echo "   Name: $NAME"
    echo "   Email: $EMAIL"
    echo "   Phone: $PHONE"
    echo "   Address: $ADDRESS"
fi
echo ""

# Product catalog
echo "📋 Generate product catalog data"
echo "   Creating 5 products with names, descriptions..."

for i in {1..5}; do
    PRODUCT_NAME=$(curl -s "$PHONEY_URL/fake/catch_phrase" | jq -r '.data // .')
    DESCRIPTION=$(curl -s "$PHONEY_URL/fake/sentence" | jq -r '.data // .')
    echo "   Product $i: $PRODUCT_NAME - $DESCRIPTION"
done
echo ""

# Testing Different Scenarios
echo "=== Testing Scenarios ==="

echo "📋 Bulk data for performance testing"
call_api "/fake/name?count=50" "Generate 50 names for bulk testing"

echo "📋 International user testing"
echo "   Testing with multiple locales..."
LOCALES=("en_US" "fr_FR" "de_DE" "es_ES" "ja_JP")
for locale in "${LOCALES[@]}"; do
    NAME_LOCAL=$(curl -s "$PHONEY_URL/fake/name?locale=$locale" | jq -r '.data // .')
    echo "   $locale: $NAME_LOCAL"
done
echo ""

echo "📋 Reproducible test data (debugging)"
echo "   Same seed should always return same result:"
echo "   First call:"
call_api "/fake/name?seed=999" ""
echo "   Second call (should be identical):"
call_api "/fake/name?seed=999" ""

# Error Handling Examples
echo "=== Error Handling ==="
echo "📋 Testing invalid generator (should return 404)"
echo "   curl \"$PHONEY_URL/fake/invalid_generator\""
echo "   Response:"
curl -s "$PHONEY_URL/fake/invalid_generator" || echo "   (Error as expected)"
echo ""

# API Information
echo "=== API Information ==="
call_api "/" "Get API information and examples"

# Tips and Tricks
echo "=== Tips and Tricks ==="
echo ""
echo "💡 Pro Tips:"
echo "   1. Use seeds for reproducible test data: ?seed=42"
echo "   2. Generate bulk data efficiently: ?count=100"
echo "   3. Test internationalization: ?locale=ja_JP"
echo "   4. Combine parameters: ?count=5&locale=fr_FR&seed=123"
echo "   5. Use jq to parse JSON: curl ... | jq '.data'"
echo ""
echo "🔍 Useful commands:"
echo "   # Find generators containing 'email':"
echo "   curl $PHONEY_URL/generators | jq '.[] | select(contains(\"email\"))'"
echo ""
echo "   # Get just the data value:"
echo "   curl -s $PHONEY_URL/fake/name | jq -r '.data'"
echo ""
echo "   # Generate test file with 100 names:"
echo "   curl -s '$PHONEY_URL/fake/name?count=100' | jq -r '.data[]' > test_names.txt"
echo ""
echo "📚 More examples: See README.md, TUTORIAL.md, and examples/ directory"
echo ""
echo "✅ Example script completed!"
echo "   Try running individual commands or modify them for your needs."
echo "   Visit $PHONEY_URL/docs for interactive API documentation."