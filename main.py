from agents.agent_engine import run_agent, confirm_action, reject_action

if __name__ == "__main__":
    print("\n🤖 NKJ EmptyNSpace AI Ready!")
    print("   Type 'quit' to exit\n")
    
    while True:
        user = input("👤 You: ").strip()
        if user.lower() in ['quit', 'exit']:
            print("👋 Goodbye!")
            break
        if not user:
            continue
        
        result = run_agent(user)
        print(f"🤖 NKJ AI: {result['response']}")
        if result.get('agents_used'):
            print(f"   Agent: {', '.join(result['agents_used'])}\n")