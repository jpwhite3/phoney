#!/usr/bin/env python3
"""
Phoney Template API Examples

This file demonstrates the full power of the Phoney bulk template system
for generating realistic test data in specific formats.
"""

import requests
import json
import time

# Configuration
PHONEY_URL = "http://localhost:8000"

def make_template_request(template_data, endpoint="/template"):
    """Helper function to make template requests."""
    print(f"📋 Making request to {endpoint}...")
    print(f"   Template: {json.dumps(template_data['template'], indent=2)[:200]}...")
    
    start_time = time.time()
    response = requests.post(f"{PHONEY_URL}{endpoint}", json=template_data)
    duration = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Generated {data['generated_count']} records in {duration:.2f}s")
        print(f"   Server processing time: {data['execution_time_ms']:.2f}ms")
        return data
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None

def example_basic_template():
    """Example 1: Basic user data template."""
    print("\n" + "="*60)
    print("🎯 Example 1: Basic User Data Template")
    print("="*60)
    
    template_data = {
        "template": {
            "name": "{{name}}",
            "email": "{{email}}",
            "phone": "{{phone}}",
            "age": "{{random_int:min=18,max=80}}"
        },
        "count": 5,
        "seed": 42  # For reproducible results
    }
    
    result = make_template_request(template_data)
    if result:
        print("Sample generated user:")
        print(json.dumps(result['data'][0], indent=2))

def example_ecommerce_template():
    """Example 2: E-commerce data with nested objects."""
    print("\n" + "="*60)
    print("🛒 Example 2: E-commerce Data Template")
    print("="*60)
    
    template_data = {
        "template": {
            "user": {
                "profile": {
                    "user_id": "{{uuid4}}",
                    "name": "{{name}}",
                    "email": "{{email}}",
                    "join_date": "{{date_between:start_date=-2y,end_date=today}}"
                },
                "address": {
                    "street": "{{street_address}}",
                    "city": "{{city}}",
                    "state": "{{state}}",
                    "zip": "{{zipcode}}",
                    "country": "{{country}}"
                }
            },
            "order": {
                "order_id": "{{uuid4}}",
                "products": "{{[catch_phrase]:count=3}}",
                "quantities": "{{[random_int]:count=3,min=1,max=5}}",
                "total": "{{pydecimal:left_digits=3,right_digits=2}}",
                "order_date": "{{date_between:start_date=-6m,end_date=today}}",
                "status": "{{random_element:elements=['pending','shipped','delivered','returned']}}"
            }
        },
        "count": 3,
        "locale": "en_US"
    }
    
    result = make_template_request(template_data)
    if result:
        print("Sample e-commerce record:")
        print(json.dumps(result['data'][0], indent=2))

def example_array_template():
    """Example 3: Arrays and bulk data generation."""
    print("\n" + "="*60)
    print("📊 Example 3: Array and Bulk Data Template")
    print("="*60)
    
    template_data = {
        "template": {
            "company": "{{company}}",
            "founded": "{{date_between:start_date=-50y,end_date=-1y}}",
            "employees": "{{[name]:count=10}}",
            "departments": "{{[word]:count=5}}",
            "locations": "{{[city]:count=3}}",
            "revenue": "{{pydecimal:left_digits=8,right_digits=2}}",
            "products": "{{[catch_phrase]:count=7}}"
        },
        "count": 2
    }
    
    result = make_template_request(template_data)
    if result:
        print("Sample company record:")
        company = result['data'][0]
        print(f"Company: {company['company']}")
        print(f"Employees: {len(company['employees'])} total")
        print(f"First 3 employees: {company['employees'][:3]}")
        print(f"Departments: {company['departments']}")

def example_international_template():
    """Example 4: Multi-locale data generation."""
    print("\n" + "="*60)
    print("🌍 Example 4: International Data Template")
    print("="*60)
    
    locales = ["en_US", "fr_FR", "de_DE", "ja_JP", "es_ES"]
    
    for locale in locales:
        print(f"\n📍 Generating data for locale: {locale}")
        
        template_data = {
            "template": {
                "name": "{{name}}",
                "address": "{{address}}",
                "phone": "{{phone}}",
                "company": "{{company}}",
                "job": "{{job}}"
            },
            "count": 1,
            "locale": locale
        }
        
        result = make_template_request(template_data)
        if result:
            person = result['data'][0]
            print(f"   Name: {person['name']}")
            print(f"   Company: {person['company']}")
            print(f"   Phone: {person['phone']}")

def example_financial_template():
    """Example 5: Financial and business data."""
    print("\n" + "="*60)
    print("💰 Example 5: Financial Data Template")
    print("="*60)
    
    template_data = {
        "template": {
            "account": {
                "account_id": "{{uuid4}}",
                "account_number": "{{random_number:digits=10}}",
                "routing_number": "{{random_number:digits=9}}",
                "balance": "{{pydecimal:left_digits=6,right_digits=2}}",
                "currency": "{{currency_code}}"
            },
            "customer": {
                "customer_id": "{{uuid4}}",
                "name": "{{name}}",
                "ssn": "{{ssn}}",
                "credit_score": "{{random_int:min=300,max=850}}",
                "income": "{{pydecimal:left_digits=6,right_digits=2}}"
            },
            "transactions": "{{[pydecimal]:count=5,left_digits=4,right_digits=2}}",
            "transaction_dates": "{{[date_between]:count=5,start_date=-1y,end_date=today}}"
        },
        "count": 2
    }
    
    result = make_template_request(template_data)
    if result:
        print("Sample financial record:")
        record = result['data'][0]
        print(f"Customer: {record['customer']['name']}")
        print(f"Account: {record['account']['account_number']}")
        print(f"Balance: ${record['account']['balance']}")
        print(f"Credit Score: {record['customer']['credit_score']}")

def example_content_template():
    """Example 6: Content and media data."""
    print("\n" + "="*60)
    print("📝 Example 6: Content Management Template")
    print("="*60)
    
    template_data = {
        "template": {
            "article": {
                "id": "{{uuid4}}",
                "title": "{{catch_phrase}}",
                "slug": "{{slug}}",
                "content": "{{text:max_nb_chars=1000}}",
                "summary": "{{text:max_nb_chars=200}}",
                "tags": "{{[word]:count=5}}",
                "category": "{{word}}",
                "published_date": "{{date_between:start_date=-1y,end_date=today}}",
                "view_count": "{{random_int:min=0,max=10000}}"
            },
            "author": {
                "author_id": "{{uuid4}}",
                "name": "{{name}}",
                "bio": "{{text:max_nb_chars=300}}",
                "social_media": {
                    "twitter": "{{user_name}}",
                    "website": "{{url}}"
                }
            },
            "comments": "{{[text]:count=3,max_nb_chars=150}}"
        },
        "count": 2
    }
    
    result = make_template_request(template_data)
    if result:
        print("Sample article:")
        article = result['data'][0]
        print(f"Title: {article['article']['title']}")
        print(f"Author: {article['author']['name']}")
        print(f"Tags: {article['article']['tags']}")
        print(f"Comments: {len(article['comments'])} total")

def example_performance_test():
    """Example 7: Performance test with larger datasets."""
    print("\n" + "="*60)
    print("⚡ Example 7: Performance Test (Large Dataset)")
    print("="*60)
    
    template_data = {
        "template": {
            "user_id": "{{uuid4}}",
            "name": "{{name}}",
            "email": "{{email}}",
            "created_at": "{{date_between:start_date=-2y,end_date=today}}"
        },
        "count": 500  # Generate 500 records
    }
    
    print("Generating 500 user records...")
    result = make_template_request(template_data)
    if result:
        print(f"Generated {len(result['data'])} records")
        print(f"Average processing time per record: {result['execution_time_ms'] / result['generated_count']:.3f}ms")

def example_validation_test():
    """Example 8: Template validation."""
    print("\n" + "="*60)
    print("🔍 Example 8: Template Validation")
    print("="*60)
    
    # Test invalid template
    invalid_template = {
        "template": {
            "name": "{{name}}",
            "invalid_field": "{{nonexistent_generator}}",
            "bad_params": "{{random_int:invalid_param=true}}"
        }
    }
    
    print("Testing template validation with invalid generators...")
    response = requests.post(f"{PHONEY_URL}/api/v1/template/validate", json=invalid_template)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Valid: {data['valid']}")
        if data['errors']:
            print("Validation errors:")
            for error in data['errors']:
                print(f"  - Field '{error['field']}': {error['message']}")
                if error['suggestions']:
                    print(f"    Suggestions: {', '.join(error['suggestions'])}")

def example_csv_export():
    """Example 9: CSV export (advanced endpoint)."""
    print("\n" + "="*60)
    print("📄 Example 9: CSV Export (Advanced Endpoint)")
    print("="*60)
    
    # Note: This requires authentication in the real API
    template_data = {
        "template": {
            "name": "{{name}}",
            "email": "{{email}}",
            "city": "{{city}}",
            "salary": "{{pydecimal:left_digits=5,right_digits=2}}"
        },
        "count": 5,
        "format": "csv"
    }
    
    print("Note: CSV export requires authentication. This is a demo of the request format.")
    print("Template for CSV generation:")
    print(json.dumps(template_data, indent=2))

def run_all_examples():
    """Run all template examples."""
    print("🚀 Phoney Template API Examples")
    print("================================")
    print("Make sure Phoney server is running at", PHONEY_URL)
    
    try:
        # Test server connection
        response = requests.get(f"{PHONEY_URL}/")
        if response.status_code != 200:
            print("❌ Could not connect to Phoney server")
            return
        
        print("✅ Connected to Phoney server")
        
        # Run examples
        example_basic_template()
        example_ecommerce_template()
        example_array_template()
        example_international_template()
        example_financial_template()
        example_content_template()
        example_performance_test()
        example_validation_test()
        example_csv_export()
        
        print("\n" + "="*60)
        print("🎉 All examples completed successfully!")
        print("="*60)
        print("\n💡 Pro Tips:")
        print("- Use seeds for reproducible test data")
        print("- Arrays are great for generating related data")
        print("- Nested objects help model complex relationships")
        print("- Try different locales for international testing")
        print("- Use validation endpoint to debug templates")
        print("\n📚 Learn more:")
        print("- Template examples: GET /template/examples")
        print("- API documentation: http://localhost:8000/docs")
        print("- Full tutorial: TUTORIAL.md")
        
    except requests.ConnectionError:
        print("❌ Could not connect to Phoney server")
        print("Please start the server: poetry run uvicorn phoney.app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_all_examples()