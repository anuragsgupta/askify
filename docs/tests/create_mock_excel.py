#!/usr/bin/env python3
"""
Create mock Excel files for testing mixed document retrieval.
"""
import pandas as pd
from datetime import datetime, timedelta
import random

# Create mock_crm_data directory if it doesn't exist
import os
os.makedirs('mock_crm_data', exist_ok=True)

# ============================================================================
# File 1: Client Pricing Sheet (with conflicts)
# ============================================================================
print("Creating client_pricing_sheet.xlsx...")

pricing_data = {
    'Client Name': [
        'Acme Corp',
        'Acme Corp',
        'TechStart Inc',
        'TechStart Inc',
        'Global Solutions Ltd',
        'Global Solutions Ltd',
        'Innovation Labs',
        'Innovation Labs'
    ],
    'Plan Type': [
        'Enterprise',
        'Enterprise (Updated)',
        'Standard',
        'Standard (Updated)',
        'Premium',
        'Premium (Updated)',
        'Basic',
        'Basic (Updated)'
    ],
    'Monthly Price': [
        '$2,500',
        '$3,200',
        '$1,200',
        '$1,500',
        '$4,500',
        '$5,000',
        '$800',
        '$950'
    ],
    'Annual Discount': [
        '15%',
        '20%',
        '10%',
        '15%',
        '25%',
        '30%',
        '5%',
        '10%'
    ],
    'Setup Fee': [
        '$1,000',
        'Waived',
        '$500',
        '$300',
        '$2,000',
        '$1,500',
        '$200',
        'Waived'
    ],
    'User Licenses': [
        50,
        75,
        25,
        30,
        100,
        120,
        10,
        15
    ],
    'Support Level': [
        'Premium 24/7',
        'Premium 24/7',
        'Business Hours',
        'Extended Hours',
        'Premium 24/7',
        'Premium 24/7',
        'Email Only',
        'Business Hours'
    ],
    'Contract Date': [
        '2023-11-15',
        '2024-01-15',
        '2023-10-20',
        '2024-02-01',
        '2023-12-01',
        '2024-01-20',
        '2023-09-15',
        '2024-01-10'
    ],
    'Status': [
        'Superseded',
        'Active',
        'Superseded',
        'Active',
        'Superseded',
        'Active',
        'Superseded',
        'Active'
    ]
}

df_pricing = pd.DataFrame(pricing_data)

# Create Excel writer
with pd.ExcelWriter('mock_crm_data/client_pricing_sheet.xlsx', engine='openpyxl') as writer:
    df_pricing.to_excel(writer, sheet_name='Pricing', index=False)
    
    # Add a summary sheet
    summary_data = {
        'Metric': ['Total Clients', 'Active Contracts', 'Total MRR', 'Average Contract Value'],
        'Value': [4, 4, '$10,650', '$2,662.50']
    }
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_excel(writer, sheet_name='Summary', index=False)

print("✅ Created client_pricing_sheet.xlsx")

# ============================================================================
# File 2: Support Tickets Database
# ============================================================================
print("Creating support_tickets_database.xlsx...")

# Generate realistic support tickets
ticket_data = {
    'Ticket ID': [f'TKT-{1000+i}' for i in range(20)],
    'Client Name': random.choices(['Acme Corp', 'TechStart Inc', 'Global Solutions Ltd', 'Innovation Labs'], k=20),
    'Issue Type': random.choices(['Billing', 'Technical', 'Feature Request', 'Bug Report', 'Account Access'], k=20),
    'Priority': random.choices(['Low', 'Medium', 'High', 'Critical'], weights=[5, 10, 4, 1], k=20),
    'Status': random.choices(['Open', 'In Progress', 'Resolved', 'Closed'], weights=[2, 3, 4, 11], k=20),
    'Created Date': [(datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d') for _ in range(20)],
    'Resolved Date': [(datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d') if random.random() > 0.3 else '' for _ in range(20)],
    'Response Time (hours)': [random.randint(1, 48) for _ in range(20)],
    'Resolution Time (hours)': [random.randint(2, 120) if random.random() > 0.3 else '' for _ in range(20)],
    'Assigned To': random.choices(['John Smith', 'Sarah Johnson', 'Mike Chen', 'Emily Davis'], k=20),
    'Customer Satisfaction': [random.choice(['⭐⭐⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐', '']) for _ in range(20)]
}

df_tickets = pd.DataFrame(ticket_data)

with pd.ExcelWriter('mock_crm_data/support_tickets_database.xlsx', engine='openpyxl') as writer:
    df_tickets.to_excel(writer, sheet_name='Tickets', index=False)
    
    # Add statistics sheet
    stats_data = {
        'Metric': [
            'Total Tickets',
            'Open Tickets',
            'Avg Response Time',
            'Avg Resolution Time',
            'Customer Satisfaction'
        ],
        'Value': [
            20,
            len(df_tickets[df_tickets['Status'] == 'Open']),
            f"{df_tickets['Response Time (hours)'].mean():.1f} hours",
            f"{pd.to_numeric(df_tickets['Resolution Time (hours)'], errors='coerce').mean():.1f} hours",
            '4.2/5.0'
        ]
    }
    df_stats = pd.DataFrame(stats_data)
    df_stats.to_excel(writer, sheet_name='Statistics', index=False)

print("✅ Created support_tickets_database.xlsx")

# ============================================================================
# File 3: Product Features Matrix
# ============================================================================
print("Creating product_features_matrix.xlsx...")

features_data = {
    'Feature': [
        'User Management',
        'API Access',
        'Custom Branding',
        'Advanced Analytics',
        'Priority Support',
        'Data Export',
        'SSO Integration',
        'Audit Logs',
        'Custom Workflows',
        'Mobile App',
        'Webhooks',
        'White Labeling'
    ],
    'Basic': ['✓', '✗', '✗', '✗', '✗', 'CSV Only', '✗', '✗', '✗', '✓', '✗', '✗'],
    'Standard': ['✓', 'Limited', '✗', 'Basic', '✗', 'CSV, JSON', '✗', '30 days', '✗', '✓', 'Limited', '✗'],
    'Premium': ['✓', '✓', '✓', 'Advanced', '✓', 'All Formats', '✓', '90 days', '✓', '✓', '✓', '✗'],
    'Enterprise': ['✓', '✓', '✓', 'Advanced', '✓', 'All Formats', '✓', 'Unlimited', '✓', '✓', '✓', '✓'],
    'Notes': [
        'Up to 10/25/100/unlimited users',
        'Rate limits apply',
        'Logo and colors',
        'Real-time dashboards',
        '24/7 phone and chat',
        'Scheduled exports available',
        'SAML 2.0 and OAuth',
        'Compliance requirement',
        'Visual workflow builder',
        'iOS and Android',
        'Real-time event notifications',
        'Complete rebrand'
    ]
}

df_features = pd.DataFrame(features_data)

with pd.ExcelWriter('mock_crm_data/product_features_matrix.xlsx', engine='openpyxl') as writer:
    df_features.to_excel(writer, sheet_name='Features', index=False)
    
    # Add pricing comparison
    pricing_comparison = {
        'Plan': ['Basic', 'Standard', 'Premium', 'Enterprise'],
        'Monthly Price': ['$800-950', '$1,200-1,500', '$4,500-5,000', '$2,500-3,200'],
        'Annual Discount': ['5-10%', '10-15%', '25-30%', '15-20%'],
        'Best For': [
            'Small teams',
            'Growing businesses',
            'Large organizations',
            'Custom requirements'
        ]
    }
    df_pricing_comp = pd.DataFrame(pricing_comparison)
    df_pricing_comp.to_excel(writer, sheet_name='Pricing', index=False)

print("✅ Created product_features_matrix.xlsx")

# ============================================================================
# File 4: Refund Policy Details (with conflicts)
# ============================================================================
print("Creating refund_policy_details.xlsx...")

refund_data = {
    'Client Name': [
        'Acme Corp',
        'Acme Corp',
        'TechStart Inc',
        'TechStart Inc',
        'Global Solutions Ltd',
        'Innovation Labs'
    ],
    'Policy Version': [
        'v1.0 (Old)',
        'v2.0 (Current)',
        'v1.0 (Old)',
        'v2.0 (Current)',
        'v2.0 (Current)',
        'v2.0 (Current)'
    ],
    'Refund Percentage': [
        '50%',
        '100%',
        '30%',
        '75%',
        '100%',
        '60%'
    ],
    'Refund Window (days)': [
        30,
        60,
        14,
        30,
        90,
        45
    ],
    'Conditions': [
        'Within 30 days, 50% refund',
        'Within 60 days, full refund',
        'Within 14 days, 30% refund',
        'Within 30 days, 75% refund',
        'Within 90 days, full refund',
        'Within 45 days, 60% refund'
    ],
    'Effective Date': [
        '2023-11-01',
        '2024-01-01',
        '2023-10-01',
        '2024-02-01',
        '2024-01-15',
        '2024-01-10'
    ],
    'Status': [
        'Superseded',
        'Active',
        'Superseded',
        'Active',
        'Active',
        'Active'
    ]
}

df_refund = pd.DataFrame(refund_data)

with pd.ExcelWriter('mock_crm_data/refund_policy_details.xlsx', engine='openpyxl') as writer:
    df_refund.to_excel(writer, sheet_name='Refund Policies', index=False)
    
    # Add policy notes
    notes_data = {
        'Note': [
            'All refund policies updated January 2024',
            'Refunds processed within 5-7 business days',
            'Setup fees are non-refundable',
            'Annual contracts have different terms',
            'Contact support@company.com for refund requests'
        ]
    }
    df_notes = pd.DataFrame(notes_data)
    df_notes.to_excel(writer, sheet_name='Notes', index=False)

print("✅ Created refund_policy_details.xlsx")

print("\n" + "="*60)
print("✅ ALL MOCK EXCEL FILES CREATED SUCCESSFULLY")
print("="*60)
print("\nFiles created in mock_crm_data/:")
print("1. client_pricing_sheet.xlsx")
print("2. support_tickets_database.xlsx")
print("3. product_features_matrix.xlsx")
print("4. refund_policy_details.xlsx")
print("\nThese files contain:")
print("- Conflicting pricing data (old vs new)")
print("- Conflicting refund policies")
print("- Support ticket history")
print("- Product feature comparisons")
print("\nUpload them with: python3 ingest_demo_data.py mock_crm_data/")
