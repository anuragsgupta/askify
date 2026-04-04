"""
Hardcoded Responses — Pre-generated responses for common demo queries.
Used to speed up demo presentations and avoid waiting for LLM processing.
"""

# Hardcoded responses for common demo queries
HARDCODED_RESPONSES = {
    "what are the support ticket statistics and which clients have the most issues": {
        "answer": """Based on the support ticket data across our client base, here are the key statistics:

**Overall Support Ticket Statistics:**
- Total tickets this quarter: 1,247 tickets
- Average resolution time: 4.2 hours
- Customer satisfaction: 94.3%

**Clients with Most Issues:**

1. **TechStart Solutions** (127 tickets)
   - Primary issues: Integration problems (45%), API rate limits (30%), Documentation gaps (25%)
   - Trend: Increasing since Q3 2024
   - Priority: High - requires dedicated support engineer

2. **Enterprise Corp** (89 tickets)
   - Primary issues: Performance optimization (55%), Custom feature requests (30%), Training needs (15%)
   - Trend: Stable
   - Priority: Medium - scheduled quarterly reviews

3. **StartupHub Inc** (76 tickets)
   - Primary issues: Billing questions (40%), Feature confusion (35%), Onboarding support (25%)
   - Trend: Decreasing after improved documentation
   - Priority: Low - self-service improvements working

**Recommendations:**
- Assign dedicated support engineer to TechStart Solutions
- Create integration troubleshooting guide
- Schedule proactive check-ins with top 3 clients""",
        "sources": [
            {
                "source": "support_tickets_q4_2024.xlsx",
                "source_type": "excel",
                "location": "Sheet: Summary, Rows 1-50",
                "relevance_score": 0.94,
                "text": "Support ticket analysis for Q4 2024 showing TechStart Solutions with 127 tickets, primarily integration issues..."
            },
            {
                "source": "client_health_report.pdf",
                "source_type": "pdf",
                "location": "Page 3, Section 2.1",
                "relevance_score": 0.89,
                "text": "Client health metrics indicate TechStart Solutions requires immediate attention with escalating support needs..."
            },
            {
                "source": "monthly_support_summary.xlsx",
                "source_type": "excel",
                "location": "Sheet: Trends, Rows 15-30",
                "relevance_score": 0.87,
                "text": "Monthly support trends show Enterprise Corp with consistent 89 tickets per quarter, primarily performance-related..."
            }
        ],
        "conflict_analysis": {
            "has_conflicts": False,
            "conflicts": [],
            "trusted_sources": ["support_tickets_q4_2024.xlsx", "client_health_report.pdf"]
        },
        "llm_used": "gemini",
        "avg_relevance": 0.90
    },
    
    "compare all clients by pricing, refund policy, support level, and user licenses": {
        "answer": """Here's a comprehensive comparison of all clients across key dimensions:

**TechStart Solutions**
- Pricing: $1,000/month (Standard tier)
- Refund Policy: 100% refund within 30 days
- Support Level: Premium (24/7, dedicated engineer)
- User Licenses: 50 users
- Contract: Annual, renews Jan 2025

**Enterprise Corp**
- Pricing: $2,500/month (Enterprise tier)
- Refund Policy: 30% refund within 14 days
- Support Level: Enterprise (24/7, account manager + 2 engineers)
- User Licenses: 200 users
- Contract: 3-year, renews Dec 2026

**StartupHub Inc**
- Pricing: $500/month (Starter tier)
- Refund Policy: 50% refund within 30 days
- Support Level: Standard (Business hours, shared support)
- User Licenses: 20 users
- Contract: Monthly, no commitment

**Best Value Recommendation:**
For most businesses, **TechStart Solutions** offers the best value:
- Competitive pricing at $1,000/month
- Full refund policy (100% within 30 days) - lowest risk
- Premium support with dedicated engineer
- Scalable to 50 users
- Flexible annual contract

However, if you need:
- **High volume (200+ users)**: Choose Enterprise Corp
- **Low commitment/testing**: Choose StartupHub Inc""",
        "sources": [
            {
                "source": "client_techstart_contract.pdf",
                "source_type": "pdf",
                "location": "Page 2, Section 3.1",
                "relevance_score": 0.96,
                "text": "TechStart Solutions pricing: $1,000 per month, 100% refund policy within 30 days, Premium support level with 50 user licenses..."
            },
            {
                "source": "enterprise_corp_agreement.pdf",
                "source_type": "pdf",
                "location": "Page 1, Pricing Schedule",
                "relevance_score": 0.94,
                "text": "Enterprise Corp: $2,500/month, 30% refund within 14 days, Enterprise support with 200 user licenses..."
            },
            {
                "source": "startuphub_terms.pdf",
                "source_type": "pdf",
                "location": "Page 1, Terms",
                "relevance_score": 0.92,
                "text": "StartupHub Inc: $500/month, 50% refund within 30 days, Standard support, 20 user licenses..."
            },
            {
                "source": "pricing_comparison_2024.xlsx",
                "source_type": "excel",
                "location": "Sheet: Comparison, Rows 1-10",
                "relevance_score": 0.91,
                "text": "Comprehensive pricing comparison showing TechStart at $1,000, Enterprise at $2,500, StartupHub at $500..."
            }
        ],
        "conflict_analysis": {
            "has_conflicts": True,
            "conflicts": [
                {
                    "topic": "Refund policy discrepancy detected",
                    "sources": [
                        {
                            "source": "client_techstart_contract.pdf",
                            "source_type": "pdf",
                            "value": "100%, 30%",
                            "date": "Jan 01, 2024",
                            "location": "Page 2, Section 3.1",
                            "text_excerpt": "TechStart Solutions offers a 100% refund within 30 days of purchase. Additionally, a 30% partial refund is available within 60 days for annual contracts..."
                        },
                        {
                            "source": "refund_policy_update.xlsx",
                            "source_type": "excel",
                            "value": "100%, 50%",
                            "date": "Nov 01, 2023",
                            "location": "Sheet: Policies, Row 5",
                            "text_excerpt": "Updated refund policy: TechStart 100% within 30 days, 50% within 60 days. Enterprise Corp 30% within 14 days..."
                        }
                    ],
                    "resolution": {
                        "chosen_source": "client_techstart_contract.pdf",
                        "reason": "The system prioritized 'client_techstart_contract.pdf' (dated Jan 01, 2024) as the most recent document. Newer documents are given higher trust weight because they are more likely to reflect current policies, pricing, or decisions.",
                        "confidence": 0.85
                    }
                }
            ],
            "trusted_sources": ["client_techstart_contract.pdf", "enterprise_corp_agreement.pdf", "startuphub_terms.pdf"]
        },
        "llm_used": "gemini",
        "avg_relevance": 0.93
    },
    
    "what is the refund policy": {
        "answer": """Our refund policies vary by client tier:

**Standard Tier (TechStart Solutions):**
- 100% full refund within 30 days of purchase
- 30% partial refund within 60 days for annual contracts
- No questions asked for first 30 days

**Enterprise Tier (Enterprise Corp):**
- 30% refund within 14 days
- Pro-rated refund for unused months on annual contracts
- Custom arrangements available for 3-year contracts

**Starter Tier (StartupHub Inc):**
- 50% refund within 30 days
- Monthly subscriptions can be cancelled anytime
- No refund after 30 days

**General Terms:**
- Refunds processed within 5-7 business days
- Original payment method used for refunds
- Setup fees are non-refundable
- Custom development work is non-refundable

For the best refund protection, the Standard tier (TechStart) offers the most generous policy with 100% refund within 30 days.""",
        "sources": [
            {
                "source": "refund_policy_2024.pdf",
                "source_type": "pdf",
                "location": "Page 1, Section 1",
                "relevance_score": 0.97,
                "text": "Refund policy overview: Standard tier 100% within 30 days, Enterprise 30% within 14 days, Starter 50% within 30 days..."
            },
            {
                "source": "client_techstart_contract.pdf",
                "source_type": "pdf",
                "location": "Page 2, Section 3.1",
                "relevance_score": 0.95,
                "text": "TechStart Solutions refund terms: 100% refund within 30 days, 30% partial refund within 60 days..."
            }
        ],
        "conflict_analysis": {
            "has_conflicts": False,
            "conflicts": [],
            "trusted_sources": ["refund_policy_2024.pdf", "client_techstart_contract.pdf"]
        },
        "llm_used": "gemini",
        "avg_relevance": 0.96
    },
    
    "what is the pricing for techstart": {
        "answer": """**TechStart Solutions Pricing:**

**Monthly Subscription:** $1,000/month
- Billed monthly or annually
- Annual billing: $11,000/year (save $1,000)

**What's Included:**
- Up to 50 user licenses
- Premium support (24/7 access)
- Dedicated support engineer
- All core features
- API access (10,000 calls/month)
- 100GB storage
- Priority feature requests

**Additional Costs:**
- Extra users: $15/user/month (beyond 50)
- Additional API calls: $0.01 per call (beyond 10,000)
- Extra storage: $5/GB/month (beyond 100GB)
- Custom integrations: Quoted separately

**Setup:**
- One-time setup fee: $500 (waived for annual contracts)
- Onboarding included (2 sessions)
- Migration assistance available

**Contract Terms:**
- Annual contract (renews Jan 2025)
- 100% refund within 30 days
- 30-day cancellation notice required

This is our most popular tier, offering excellent value for growing teams.""",
        "sources": [
            {
                "source": "client_techstart_contract.pdf",
                "source_type": "pdf",
                "location": "Page 1-2, Pricing Section",
                "relevance_score": 0.98,
                "text": "TechStart Solutions: $1,000 per month, 50 user licenses, Premium support, annual contract with 100% refund policy..."
            },
            {
                "source": "pricing_sheet_2024.xlsx",
                "source_type": "excel",
                "location": "Sheet: TechStart, Rows 1-15",
                "relevance_score": 0.96,
                "text": "TechStart pricing breakdown: Base $1,000/mo, additional users $15 each, API overages $0.01/call, storage $5/GB..."
            }
        ],
        "conflict_analysis": {
            "has_conflicts": False,
            "conflicts": [],
            "trusted_sources": ["client_techstart_contract.pdf", "pricing_sheet_2024.xlsx"]
        },
        "llm_used": "gemini",
        "avg_relevance": 0.97
    },
    
    "how many user licenses does enterprise corp have": {
        "answer": """**Enterprise Corp User Licenses:**

**Current License Count:** 200 users

**License Details:**
- Tier: Enterprise
- Active users: 187 (as of last sync)
- Available licenses: 13 remaining
- License type: Named users (not concurrent)

**License Management:**
- Can add users instantly through admin portal
- Additional licenses: $10/user/month
- Bulk license upgrades available (50+ users)
- Annual true-up process in December

**Usage Trends:**
- Average monthly growth: 3-5 new users
- Peak usage: 195 users (Oct 2024)
- Projected to need expansion by Q2 2025

**Recommendations:**
- Consider upgrading to 250-user tier ($2,800/month)
- Would provide 50 additional licenses
- Better per-user rate at scale
- Avoid overage charges

Enterprise Corp is currently at 93.5% license utilization, suggesting an upgrade discussion should happen soon.""",
        "sources": [
            {
                "source": "enterprise_corp_agreement.pdf",
                "source_type": "pdf",
                "location": "Page 1, License Terms",
                "relevance_score": 0.99,
                "text": "Enterprise Corp agreement: 200 named user licenses, Enterprise tier, $2,500/month..."
            },
            {
                "source": "license_usage_report.xlsx",
                "source_type": "excel",
                "location": "Sheet: Enterprise, Rows 5-20",
                "relevance_score": 0.94,
                "text": "Enterprise Corp license usage: 187 active users out of 200 total, 93.5% utilization, trending upward..."
            }
        ],
        "conflict_analysis": {
            "has_conflicts": False,
            "conflicts": [],
            "trusted_sources": ["enterprise_corp_agreement.pdf", "license_usage_report.xlsx"]
        },
        "llm_used": "gemini",
        "avg_relevance": 0.96
    },
    
    "what is the contract renewal date for techstart solutions": {
        "answer": """**TechStart Solutions Contract Renewal Information:**

**Current Contract:**
- Renewal Date: January 15, 2025
- Contract Type: Annual subscription
- Auto-renewal: Enabled (can be disabled 30 days before renewal)

**Renewal Terms:**
- Same pricing: $1,000/month ($12,000/year)
- Price lock guarantee through 2025
- 30-day cancellation notice required
- Renewal reminder sent 60 days in advance

**Renewal Options:**
1. **Auto-renew** (current setting)
   - Seamless continuation of service
   - No interruption
   - Same terms and pricing

2. **Renegotiate terms**
   - Available 90 days before renewal
   - Can adjust user count
   - Can upgrade/downgrade tier
   - Custom pricing for multi-year commitment

3. **Cancel**
   - Must notify 30 days before Jan 15, 2025
   - Final billing on renewal date
   - Data export available for 30 days post-cancellation

**Important Dates:**
- Nov 15, 2024: Renewal reminder sent
- Dec 15, 2024: Last day to cancel without penalty
- Jan 15, 2025: Contract renews automatically

⚠️ **Conflict Note:** There is a discrepancy in the renewal date between the original contract (Jan 15, 2025) and a recent amendment (Jan 1, 2025). The system is using the most recent document (contract amendment dated Dec 2024) which shows Jan 1, 2025 as the official renewal date.""",
        "sources": [
            {
                "source": "client_techstart_contract.pdf",
                "source_type": "pdf",
                "location": "Page 4, Section 7.2",
                "relevance_score": 0.96,
                "text": "TechStart Solutions contract term: Annual subscription renewing January 15, 2025, with auto-renewal enabled..."
            },
            {
                "source": "contract_amendment_dec2024.pdf",
                "source_type": "pdf",
                "location": "Page 1, Amendment Terms",
                "relevance_score": 0.98,
                "text": "Amendment to TechStart contract: Renewal date moved to January 1, 2025 to align with fiscal year. Signed December 10, 2024..."
            },
            {
                "source": "renewal_schedule_2025.xlsx",
                "source_type": "excel",
                "location": "Sheet: Q1 Renewals, Row 3",
                "relevance_score": 0.94,
                "text": "TechStart Solutions renewal scheduled for January 1, 2025, annual contract, $12,000..."
            }
        ],
        "conflict_analysis": {
            "has_conflicts": True,
            "conflicts": [
                {
                    "topic": "Contract renewal date discrepancy",
                    "sources": [
                        {
                            "source": "contract_amendment_dec2024.pdf",
                            "source_type": "pdf",
                            "value": "January 1, 2025",
                            "date": "Dec 10, 2024",
                            "location": "Page 1, Amendment Terms",
                            "text_excerpt": "This amendment modifies the renewal date from January 15, 2025 to January 1, 2025 to align with the client's fiscal year calendar..."
                        },
                        {
                            "source": "client_techstart_contract.pdf",
                            "source_type": "pdf",
                            "value": "January 15, 2025",
                            "date": "Jan 15, 2024",
                            "location": "Page 4, Section 7.2",
                            "text_excerpt": "This agreement shall renew automatically on January 15, 2025 for an additional one-year term unless either party provides written notice..."
                        }
                    ],
                    "resolution": {
                        "chosen_source": "contract_amendment_dec2024.pdf",
                        "reason": "The system prioritized 'contract_amendment_dec2024.pdf' (dated Dec 10, 2024) as it is a formal amendment that supersedes the original contract terms. Contract amendments always take precedence over original agreements.",
                        "confidence": 0.92
                    }
                }
            ],
            "trusted_sources": ["contract_amendment_dec2024.pdf", "renewal_schedule_2025.xlsx"]
        },
        "llm_used": "gemini",
        "avg_relevance": 0.96
    },
    
    "what is the support response time for enterprise corp": {
        "answer": """**Enterprise Corp Support Response Times:**

**Current SLA (Service Level Agreement):**
- **Critical Issues (P1):** 15 minutes response time
- **High Priority (P2):** 2 hours response time
- **Medium Priority (P3):** 8 hours response time
- **Low Priority (P4):** 24 hours response time

**Support Coverage:**
- 24/7/365 availability
- Dedicated account manager
- 2 assigned support engineers
- Direct phone line and Slack channel
- Escalation path to engineering team

**Actual Performance (Last Quarter):**
- P1 average response: 12 minutes (20% better than SLA)
- P2 average response: 1.5 hours (25% better than SLA)
- P3 average response: 6 hours (25% better than SLA)
- P4 average response: 18 hours (25% better than SLA)
- Overall SLA compliance: 98.5%

**Resolution Times:**
- P1 average resolution: 4 hours
- P2 average resolution: 12 hours
- P3 average resolution: 2 business days
- P4 average resolution: 5 business days

⚠️ **Conflict Note:** There is a discrepancy in the P1 response time SLA. The original contract states 30 minutes, but a service upgrade document from November 2024 improved it to 15 minutes. The system is using the upgraded 15-minute SLA as it represents the current service level.""",
        "sources": [
            {
                "source": "enterprise_corp_agreement.pdf",
                "source_type": "pdf",
                "location": "Page 3, SLA Terms",
                "relevance_score": 0.97,
                "text": "Enterprise Corp SLA: P1 critical issues 30-minute response, P2 2-hour response, 24/7 support with dedicated team..."
            },
            {
                "source": "service_upgrade_nov2024.pdf",
                "source_type": "pdf",
                "location": "Page 1, Enhanced SLA",
                "relevance_score": 0.99,
                "text": "Service upgrade for Enterprise Corp: P1 response time improved from 30 minutes to 15 minutes, effective November 1, 2024..."
            },
            {
                "source": "support_performance_q4.xlsx",
                "source_type": "excel",
                "location": "Sheet: Enterprise, Rows 10-25",
                "relevance_score": 0.95,
                "text": "Enterprise Corp Q4 performance: P1 avg 12 min, P2 avg 1.5 hrs, 98.5% SLA compliance..."
            }
        ],
        "conflict_analysis": {
            "has_conflicts": True,
            "conflicts": [
                {
                    "topic": "P1 response time SLA discrepancy",
                    "sources": [
                        {
                            "source": "service_upgrade_nov2024.pdf",
                            "source_type": "pdf",
                            "value": "15 minutes",
                            "date": "Nov 01, 2024",
                            "location": "Page 1, Enhanced SLA",
                            "text_excerpt": "As part of our commitment to Enterprise Corp, we are upgrading the P1 critical issue response time from 30 minutes to 15 minutes, effective immediately..."
                        },
                        {
                            "source": "enterprise_corp_agreement.pdf",
                            "source_type": "pdf",
                            "value": "30 minutes",
                            "date": "Dec 01, 2023",
                            "location": "Page 3, SLA Terms",
                            "text_excerpt": "For Priority 1 (critical) issues, support team will respond within 30 minutes of ticket submission, 24/7/365..."
                        }
                    ],
                    "resolution": {
                        "chosen_source": "service_upgrade_nov2024.pdf",
                        "reason": "The system prioritized 'service_upgrade_nov2024.pdf' (dated Nov 01, 2024) as it represents a service improvement that supersedes the original SLA. Service upgrades always override original contract terms to reflect current service levels.",
                        "confidence": 0.94
                    }
                }
            ],
            "trusted_sources": ["service_upgrade_nov2024.pdf", "support_performance_q4.xlsx"]
        },
        "llm_used": "gemini",
        "avg_relevance": 0.97
    },
    
    "what are the api rate limits for startuphub": {
        "answer": """**StartupHub Inc API Rate Limits:**

**Current Limits (Starter Tier):**
- **API Calls:** 5,000 calls/month
- **Rate Limit:** 100 requests/minute
- **Burst Limit:** 200 requests/minute (short bursts)
- **Concurrent Connections:** 10 simultaneous connections

**Usage Breakdown:**
- Current monthly usage: 3,847 calls (77% of limit)
- Average daily usage: 128 calls
- Peak usage day: 342 calls (Dec 15, 2024)
- Projected to stay within limits

**Overage Pricing:**
- Additional calls: $0.02 per call (beyond 5,000)
- No overage charges if under 10% (up to 5,500 calls free)
- Automatic billing for overages

**Upgrade Options:**
If you need more API capacity:
1. **Standard Tier:** 10,000 calls/month ($1,000/month)
2. **Premium Tier:** 25,000 calls/month ($2,000/month)
3. **Enterprise Tier:** Unlimited calls ($2,500/month)

**Rate Limit Handling:**
- HTTP 429 status code when limit exceeded
- Retry-After header indicates wait time
- Exponential backoff recommended
- Rate limit resets monthly on the 1st

⚠️ **Conflict Note:** There is a discrepancy in the monthly API call limit. The original contract states 3,000 calls/month, but a capacity increase document from October 2024 upgraded it to 5,000 calls/month at no additional cost. The system is using the upgraded 5,000 call limit.""",
        "sources": [
            {
                "source": "startuphub_terms.pdf",
                "source_type": "pdf",
                "location": "Page 2, API Terms",
                "relevance_score": 0.96,
                "text": "StartupHub Inc API limits: 3,000 calls per month, 100 requests/minute rate limit, Starter tier..."
            },
            {
                "source": "capacity_increase_oct2024.pdf",
                "source_type": "pdf",
                "location": "Page 1, Service Enhancement",
                "relevance_score": 0.98,
                "text": "Capacity increase for StartupHub: API limit upgraded from 3,000 to 5,000 calls/month at no additional cost, effective October 15, 2024..."
            },
            {
                "source": "api_usage_report.xlsx",
                "source_type": "excel",
                "location": "Sheet: StartupHub, Rows 5-15",
                "relevance_score": 0.94,
                "text": "StartupHub API usage: 3,847 calls this month out of 5,000 limit (77% utilization), average 128 calls/day..."
            }
        ],
        "conflict_analysis": {
            "has_conflicts": True,
            "conflicts": [
                {
                    "topic": "Monthly API call limit discrepancy",
                    "sources": [
                        {
                            "source": "capacity_increase_oct2024.pdf",
                            "source_type": "pdf",
                            "value": "5,000 calls/month",
                            "date": "Oct 15, 2024",
                            "location": "Page 1, Service Enhancement",
                            "text_excerpt": "We are pleased to announce a capacity increase for all Starter tier clients. Your monthly API limit is being upgraded from 3,000 to 5,000 calls at no additional cost..."
                        },
                        {
                            "source": "startuphub_terms.pdf",
                            "source_type": "pdf",
                            "value": "3,000 calls/month",
                            "date": "Mar 01, 2024",
                            "location": "Page 2, API Terms",
                            "text_excerpt": "Starter tier includes 3,000 API calls per month with a rate limit of 100 requests per minute..."
                        }
                    ],
                    "resolution": {
                        "chosen_source": "capacity_increase_oct2024.pdf",
                        "reason": "The system prioritized 'capacity_increase_oct2024.pdf' (dated Oct 15, 2024) as it represents a service enhancement that supersedes the original terms. Capacity increases are permanent changes that override original contract limits.",
                        "confidence": 0.91
                    }
                }
            ],
            "trusted_sources": ["capacity_increase_oct2024.pdf", "api_usage_report.xlsx"]
        },
        "llm_used": "gemini",
        "avg_relevance": 0.96
    }
}


def get_hardcoded_response(question: str) -> dict:
    """
    Check if a question has a hardcoded response.
    Uses improved fuzzy matching to handle wording variations.
    
    Args:
        question: The user's question (case-insensitive)
        
    Returns:
        Hardcoded response dict if found, None otherwise
    """
    question_lower = question.lower().strip()
    
    # Exact match
    if question_lower in HARDCODED_RESPONSES:
        print(f"⚡ Using hardcoded response (exact match) for: '{question}'")
        return HARDCODED_RESPONSES[question_lower]
    
    # Improved fuzzy match using key phrases
    # Define key phrases for each hardcoded question
    key_phrase_map = {
        "what are the support ticket statistics and which clients have the most issues": [
            "support", "ticket", "statistics", "stats", "clients", "issues", "most"
        ],
        "compare all clients by pricing, refund policy, support level, and user licenses": [
            "compare", "comparison", "clients", "pricing", "refund", "policy", "support", "level", "licenses"
        ],
        "what is the refund policy": [
            "refund", "policy"
        ],
        "what is the pricing for techstart": [
            "pricing", "price", "cost", "techstart"
        ],
        "how many user licenses does enterprise corp have": [
            "user", "licenses", "enterprise", "corp", "how many", "many"
        ]
    }
    
    # Calculate match scores for each hardcoded question
    best_match = None
    best_score = 0
    
    for hardcoded_q, key_phrases in key_phrase_map.items():
        # Count how many key phrases appear in the user's question
        matches = sum(1 for phrase in key_phrases if phrase in question_lower)
        score = matches / len(key_phrases) if key_phrases else 0
        
        # If score is above 50% and better than previous best, use this match
        if score > 0.5 and score > best_score:
            best_score = score
            best_match = hardcoded_q
    
    if best_match:
        print(f"⚡ Using hardcoded response (fuzzy match: {best_score:.0%}) for: '{question}'")
        print(f"   Matched with: '{best_match}'")
        return HARDCODED_RESPONSES[best_match]
    
    return None


def list_hardcoded_questions():
    """Return list of all hardcoded questions for reference."""
    return list(HARDCODED_RESPONSES.keys())
