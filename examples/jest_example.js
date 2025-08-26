/**
 * Example: Using Phoney with Jest for JavaScript testing
 * Run with: npm test examples/jest_example.js
 * 
 * First install dependencies: npm install axios jest
 */

const axios = require('axios');

// Configuration
const PHONEY_BASE_URL = 'http://localhost:8000';

class PhoneyClient {
    constructor(baseUrl = PHONEY_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    async fake(generator, options = {}) {
        const params = new URLSearchParams(options);
        const url = `${this.baseUrl}/fake/${generator}?${params}`;
        const response = await axios.get(url);
        return response.data.data;
    }

    async fakeBulk(generator, count, options = {}) {
        return this.fake(generator, { ...options, count });
    }
}

// Global client instance
const phoney = new PhoneyClient();

// Mock functions representing your application code
function registerUser(name, email, phone = null) {
    if (!name || !email) {
        throw new Error('Name and email required');
    }
    if (!email.includes('@')) {
        throw new Error('Invalid email format');
    }
    
    return {
        id: Math.abs(hash(email) % 10000),
        name,
        email,
        phone,
        status: 'active'
    };
}

function createProduct(name, price, description = null) {
    if (price <= 0) {
        throw new Error('Price must be positive');
    }
    
    return {
        id: Math.abs(hash(name) % 10000),
        name,
        price,
        description,
        inStock: true
    };
}

// Simple hash function for mocking IDs
function hash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32-bit integer
    }
    return hash;
}

// Test Suites

describe('User Registration', () => {
    test('should register user with valid fake data', async () => {
        const name = await phoney.fake('name');
        const email = await phoney.fake('email');
        const phone = await phoney.fake('phone');
        
        const user = registerUser(name, email, phone);
        
        expect(user.name).toBe(name);
        expect(user.email).toBe(email);
        expect(user.phone).toBe(phone);
        expect(user.status).toBe('active');
        expect(user.id).toBeGreaterThan(0);
    });

    test('should handle international users', async () => {
        const locales = ['en_US', 'fr_FR', 'de_DE', 'ja_JP', 'es_ES'];
        
        for (const locale of locales) {
            const name = await phoney.fake('name', { locale });
            const email = await phoney.fake('email');
            
            const user = registerUser(name, email);
            expect(user.name).toBe(name);
            expect(user.name.length).toBeGreaterThan(0);
        }
    });

    test('should handle bulk user registration', async () => {
        const names = await phoney.fakeBulk('name', 10);
        const emails = await phoney.fakeBulk('email', 10);
        
        const users = [];
        for (let i = 0; i < names.length; i++) {
            const user = registerUser(names[i], emails[i]);
            users.push(user);
        }
        
        expect(users).toHaveLength(10);
        
        // Check all emails are unique
        const uniqueEmails = new Set(users.map(u => u.email));
        expect(uniqueEmails.size).toBe(10);
    });

    test('should produce reproducible results with seeds', async () => {
        const name1 = await phoney.fake('name', { seed: 42 });
        const email1 = await phoney.fake('email', { seed: 123 });
        
        const name2 = await phoney.fake('name', { seed: 42 });
        const email2 = await phoney.fake('email', { seed: 123 });
        
        expect(name1).toBe(name2);
        expect(email1).toBe(email2);
    });

    test('should reject invalid emails', async () => {
        const name = await phoney.fake('name');
        const invalidEmails = ['', 'invalid', 'no-at-symbol', '@domain.com'];
        
        for (const invalidEmail of invalidEmails) {
            expect(() => {
                registerUser(name, invalidEmail);
            }).toThrow('Invalid email format');
        }
    });
});

describe('Product Management', () => {
    test('should create product with fake data', async () => {
        const name = await phoney.fake('catch_phrase');
        const description = await phoney.fake('text');
        const price = parseFloat(await phoney.fake('pydecimal'));
        
        const product = createProduct(name, Math.abs(price), description);
        
        expect(product.name).toBe(name);
        expect(product.price).toBeGreaterThan(0);
        expect(product.description).toBe(description);
        expect(product.inStock).toBe(true);
    });

    test('should create product catalog', async () => {
        const names = await phoney.fakeBulk('catch_phrase', 20);
        const descriptions = await phoney.fakeBulk('paragraph', 20);
        
        const products = [];
        for (let i = 0; i < names.length; i++) {
            const price = Math.random() * 100 + 1; // Random price 1-101
            const product = createProduct(names[i], price, descriptions[i]);
            products.push(product);
        }
        
        expect(products).toHaveLength(20);
        expect(products.every(p => p.price > 0)).toBe(true);
        
        // Check names are mostly unique
        const uniqueNames = new Set(products.map(p => p.name));
        expect(uniqueNames.size).toBeGreaterThan(15);
    });
});

describe('E-commerce Flow', () => {
    test('should complete purchase flow with fake data', async () => {
        // Generate customer data
        const customer = {
            name: await phoney.fake('name'),
            email: await phoney.fake('email'),
            phone: await phoney.fake('phone'),
            address: await phoney.fake('address'),
        };
        
        // Generate product data
        const products = [];
        const productNames = await phoney.fakeBulk('catch_phrase', 3);
        
        for (const name of productNames) {
            const product = createProduct(
                name,
                Math.random() * 50 + 10, // Price between 10-60
                await phoney.fake('sentence')
            );
            products.append(product);
        }
        
        // Verify all data is generated
        expect(customer.name).toBeTruthy();
        expect(customer.email).toContain('@');
        expect(products).toHaveLength(3);
        expect(products.every(p => p.price > 0)).toBe(true);
    });
});

describe('Performance Testing', () => {
    test('should handle bulk data generation efficiently', async () => {
        const startTime = Date.now();
        
        // Generate large dataset
        const names = await phoney.fakeBulk('name', 100);
        const emails = await phoney.fakeBulk('email', 100);
        
        const users = [];
        for (let i = 0; i < names.length; i++) {
            const user = registerUser(names[i], emails[i]);
            users.append(user);
        }
        
        const duration = Date.now() - startTime;
        
        expect(users).toHaveLength(100);
        expect(duration).toBeLessThan(10000); // Should complete within 10 seconds
    }, 15000); // Extend timeout for performance test
});

// Test utilities and helpers

describe('Phoney Client', () => {
    test('should connect to Phoney API', async () => {
        const name = await phoney.fake('name');
        expect(typeof name).toBe('string');
        expect(name.length).toBeGreaterThan(0);
    });

    test('should handle API errors gracefully', async () => {
        await expect(phoney.fake('nonexistent_generator')).rejects.toThrow();
    });

    test('should support all common generators', async () => {
        const generators = [
            'name', 'email', 'phone', 'address', 'company',
            'job', 'date', 'time', 'url', 'text'
        ];
        
        for (const generator of generators) {
            const result = await phoney.fake(generator);
            expect(result).toBeTruthy();
        }
    });
});

// Setup and teardown
beforeAll(() => {
    console.log('Starting Phoney integration tests...');
    console.log('Make sure Phoney server is running at', PHONEY_BASE_URL);
});

afterAll(() => {
    console.log('Phoney integration tests completed!');
});

module.exports = { PhoneyClient, registerUser, createProduct };