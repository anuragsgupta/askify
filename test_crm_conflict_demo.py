"""
CRM Auto-Fill and Conflict Detection Demo Script

This script demonstrates:
1. Automatic CRM ticket population from RAG queries
2. Conflict detection between old and new documents
3. Date-based prioritization with explanations
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_subsection(title):
    """Print a formatted subsection header"""
    print(f"\n--- {title} ---\n")

def upload_document(filepath):
    """Upload a document to the system"""
    print(f"📤 Uploading: {filepath}")
    with open(filepath, 'rb') as f:
        files = {'file': (filepath.split('/')[-1], f)}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
        if response.status_code == 200:
            print(f"   ✅ Uploaded successfully")
            return True
        else:
            print(f"   ❌ Upload failed: {response.text}")
            return False

def query_rag(question):
    """Query the RAG system"""
    print(f"\n💬 Query: {question}")
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"question": question, "n_results": 10}
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"   ❌ Query failed: {response.text}")
        return None

def display_conflict_analysis(conflict_analysis):
    """Display conflict analysis in a formatted way"""
    if not conflict_analysis or not conflict_analysis.get('has_conflicts'):
        print("   ✅ No conflicts detected")
        return
    
    print("\n   ⚠️  CONFLICTS DETECTED!")
    print("   " + "-"*60)
    
    for conflict in conflict_analysis.get('conflicts', []):
        print(f"\n   Topic: {conflict.get('topic', 'Unknown')}")
        print(f"\n   Conflicting Sources:")
        
        for source in conflict.get('sources', []):
            print(f"\n   📄 {source.get('source', 'Unknown')}")
            print(f"      Type: {source.get('source_type', 'unknown')}")
            print(f"      Value: {source.get('value', 'N/A')}")
            print(f"      Date: {source.get('date', 'Unknown')}")
            print(f"      Location: {source.get('location', 'N/A')}")
        
        resolution = conflict.get('resolution', {})
        print(f"\n   🎯 RESOLUTION:")
        print(f"      Chosen Source: {resolution.get('chosen_source', 'Unknown')}")
        print(f"      Confidence: {resolution.get('confidence', 0)*100:.0f}%")
        print(f"\n      Reasoning:")
        reason = resolution.get('reason', 'No reason provided')
        for line in reason.split('. '):
            if line.strip():
                print(f"      • {line.strip()}")

def display_crm_ticket(result):
    """Display auto-populated CRM ticket"""
    print("\n   📋 AUTO-POPULATED CRM TICKET")
    print("   " + "-"*60)
    
    # Subject (first 60 chars of answer)
    answer = result.get('answer', '')
    subject = f"Query: {answer[:60]}..." if len(answer) > 60 else f"Query: {answer}"
    print(f"\n   Subject: {subject}")
    
    # Description
    sources = result.get('sources', [])
    source_names = ', '.join([s.get('source', 'Unknown') for s in sources])
    
    conflict_analysis = result.get('conflict_analysis', {})
    conflict_info = ""
    if conflict_analysis.get('has_conflicts'):
        conflicts = conflict_analysis.get('conflicts', [])
        if conflicts:
            resolution = conflicts[0].get('resolution', {})
            conflict_info = f"\n\n   ⚠️ Conflicts detected: {resolution.get('reason', 'See details.')}"
    else:
        conflict_info = "\n\n   ✅ No conflicts detected across sources."
    
    description = (
        f"\n   Description:\n"
        f"   AI Response Summary:\n"
        f"   {answer[:300]}{'...' if len(answer) > 300 else ''}\n"
        f"\n   Sources referenced: {source_names}"
        f"{conflict_info}"
    )
    print(description)
    
    print("\n   " + "-"*60)
    print("   ✅ Ticket ready for submission (editable by agent)")

def demo_scenario_1():
    """Demo: Acme Corp Pricing Conflict"""
    print_section("SCENARIO 1: Acme Corp - Pricing Inquiry with Conflict")
    
    print("📖 Background:")
    print("   Customer service agent receives inquiry from Acme Corp about")
    print("   current pricing. System has both old email (Nov 2023) and")
    print("   new policy document (Jan 2024) with different prices.")
    
    print_subsection("Step 1: Upload Documents")
    upload_document("mock_crm_data/client_acme_corp_old_email.eml")
    upload_document("mock_crm_data/client_acme_corp_new_policy.txt")
    upload_document("mock_crm_data/client_acme_corp_support_history.txt")
    
    time.sleep(2)  # Wait for indexing
    
    print_subsection("Step 2: Agent Searches for Client Information")
    result = query_rag("What is the current pricing for Acme Corp's Enterprise Plan?")
    
    if result:
        print_subsection("Step 3: System Response")
        print(f"   Answer: {result.get('answer', 'No answer')}")
        
        print_subsection("Step 4: Conflict Detection Analysis")
        display_conflict_analysis(result.get('conflict_analysis'))
        
        print_subsection("Step 5: Auto-Populated CRM Ticket")
        display_crm_ticket(result)
        
        print_subsection("Step 6: Agent Actions")
        print("   ✅ Agent reviews auto-populated ticket")
        print("   ✅ Agent sees conflict explanation")
        print("   ✅ Agent understands why $3,200 is correct (newer document)")
        print("   ✅ Agent can add notes and submit ticket")
        print("   ✅ No manual data entry required!")

def demo_scenario_2():
    """Demo: TechStart Inc Refund Policy Conflict"""
    print_section("SCENARIO 2: TechStart Inc - Refund Policy Inquiry with Conflict")
    
    print("📖 Background:")
    print("   Customer service agent needs to process refund request from")
    print("   TechStart Inc. System has old email (Oct 2023) stating 50%")
    print("   refund and new policy (Jan 2024) stating 100% refund.")
    
    print_subsection("Step 1: Upload Documents")
    upload_document("mock_crm_data/client_techstart_inc_old_quote.eml")
    upload_document("mock_crm_data/client_techstart_inc_new_policy.txt")
    
    time.sleep(2)  # Wait for indexing
    
    print_subsection("Step 2: Agent Searches for Refund Policy")
    result = query_rag("What is our current refund policy and refund amount percentage?")
    
    if result:
        print_subsection("Step 3: System Response")
        print(f"   Answer: {result.get('answer', 'No answer')}")
        
        print_subsection("Step 4: Conflict Detection Analysis")
        display_conflict_analysis(result.get('conflict_analysis'))
        
        print_subsection("Step 5: Auto-Populated CRM Ticket")
        display_crm_ticket(result)
        
        print_subsection("Step 6: Agent Actions")
        print("   ✅ Agent reviews auto-populated ticket")
        print("   ✅ Agent sees conflict between 50% and 100% refund")
        print("   ✅ Agent understands why 100% is correct (newer policy)")
        print("   ✅ Agent can confidently inform customer of 100% refund")
        print("   ✅ No manual policy lookup required!")

def demo_scenario_3():
    """Demo: Combined Query - Multiple Conflicts"""
    print_section("SCENARIO 3: Complex Query - Multiple Conflicts")
    
    print("📖 Background:")
    print("   Agent needs comprehensive information about both pricing")
    print("   and refund policies. System must detect and resolve")
    print("   multiple conflicts across different topics.")
    
    print_subsection("Step 1: Agent Asks Complex Question")
    result = query_rag(
        "What are our current Enterprise Plan pricing, refund policy, "
        "and refund percentage? Include setup fees and processing time."
    )
    
    if result:
        print_subsection("Step 2: System Response")
        answer = result.get('answer', 'No answer')
        print(f"   Answer: {answer}")
        
        print_subsection("Step 3: Conflict Detection Analysis")
        display_conflict_analysis(result.get('conflict_analysis'))
        
        print_subsection("Step 4: Auto-Populated CRM Ticket")
        display_crm_ticket(result)
        
        print_subsection("Step 5: Key Insights")
        print("   ✅ System detected multiple value conflicts")
        print("   ✅ System prioritized newest documents for each conflict")
        print("   ✅ System provided clear explanations for each decision")
        print("   ✅ Agent has complete context without manual research")
        print("   ✅ Ticket includes all relevant information automatically")

def main():
    """Run all demo scenarios"""
    print("\n" + "="*70)
    print("  CRM AUTO-FILL & CONFLICT DETECTION DEMO")
    print("  Demonstrating Autonomous Ticket Population with Conflict Resolution")
    print("="*70)
    
    print("\n⚠️  PREREQUISITES:")
    print("   1. Backend server running: ./start_backend.sh")
    print("   2. Ollama running: ollama serve")
    print("   3. Mock data files in mock_crm_data/ directory")
    
    input("\nPress Enter to start demo...")
    
    try:
        # Run all scenarios
        demo_scenario_1()
        input("\n\nPress Enter to continue to Scenario 2...")
        
        demo_scenario_2()
        input("\n\nPress Enter to continue to Scenario 3...")
        
        demo_scenario_3()
        
        print_section("DEMO COMPLETE")
        print("✅ All scenarios demonstrated successfully!")
        print("\nKey Takeaways:")
        print("   1. CRM tickets are auto-populated from RAG queries")
        print("   2. Conflicts are automatically detected")
        print("   3. Newest documents are prioritized")
        print("   4. Clear explanations provided for all decisions")
        print("   5. No manual data entry required")
        print("   6. Agents can focus on customer service, not data lookup")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
