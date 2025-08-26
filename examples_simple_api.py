#!/usr/bin/env python3
"""
Examples of using the Phoney Simple API for beginners.
This demonstrates how easy it is to generate fake data for testing.
"""

import requests
import json

# Base URL for the API (adjust if needed)
BASE_URL = "http://localhost:8000"

def example_basic_generation():
    """Basic examples of generating fake data."""
    print("=== Basic Data Generation ===")
    
    examples = [
        "name",
        "email", 
        "phone",
        "address",
        "company"
    ]
    
    for generator in examples:
        response = requests.get(f"{BASE_URL}/fake/{generator}")
        if response.status_code == 200:
            data = response.json()
            print(f"{generator.title()}: {data['data']}")

def example_multiple_items():
    """Generate multiple items at once."""
    print("\n=== Multiple Items ===")
    
    response = requests.get(f"{BASE_URL}/fake/name?count=5")
    if response.status_code == 200:
        data = response.json()
        print(f"5 Names: {data['data']}")

def example_localized_data():
    """Generate locale-specific data."""
    print("\n=== Localized Data ===")
    
    locales = ["en_US", "fr_FR", "de_DE", "es_ES"]
    
    for locale in locales:
        response = requests.get(f"{BASE_URL}/fake/name?locale={locale}")
        if response.status_code == 200:
            data = response.json()
            print(f"{locale}: {data['data']}")

def example_reproducible_data():
    """Generate reproducible data using seeds."""
    print("\n=== Reproducible Data (with seed) ===")
    
    # Same seed should produce same results
    for i in range(2):
        response = requests.get(f"{BASE_URL}/fake/name?seed=42&count=3")
        if response.status_code == 200:
            data = response.json()
            print(f"Run {i+1} with seed 42: {data['data']}")

def list_available_generators():
    """Show available generators."""
    print("\n=== Available Generators ===")
    
    response = requests.get(f"{BASE_URL}/generators")
    if response.status_code == 200:
        generators = response.json()
        print(f"Total generators available: {len(generators)}")
        print("Common generators:", generators[:20])

def create_test_user_data():
    """Example: Create complete test user data."""
    print("\n=== Creating Test User Data ===")
    
    user_fields = {
        "name": "name",
        "email": "email", 
        "phone": "phone",
        "address": "address",
        "company": "company",
        "job": "job"
    }
    
    user_data = {}
    for field, generator in user_fields.items():
        response = requests.get(f"{BASE_URL}/fake/{generator}?seed=123")
        if response.status_code == 200:
            data = response.json()
            user_data[field] = data['data']
    
    print("Complete test user:")
    print(json.dumps(user_data, indent=2))

if __name__ == "__main__":
    print("Phoney Simple API Examples")
    print("Make sure the server is running: poetry run uvicorn phoney.app.main:app --reload")
    print()
    
    try:
        example_basic_generation()
        example_multiple_items()
        example_localized_data()
        example_reproducible_data()
        list_available_generators()
        create_test_user_data()
        
        print("\n✅ All examples completed successfully!")
        print("\nTry these URLs in your browser:")
        print("- http://localhost:8000/fake/name")
        print("- http://localhost:8000/fake/email?count=5")
        print("- http://localhost:8000/generators")
        print("- http://localhost:8000/docs (API documentation)")
        
    except requests.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("Please start the server with: poetry run uvicorn phoney.app.main:app --reload")
    except Exception as e:
        print(f"❌ An error occurred: {e}")