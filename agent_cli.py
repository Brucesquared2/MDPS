import sys
from agent_core import AgentCore

def main():
    agent = AgentCore()

    print("\n=== MDPS CLI Agent ===")
    print("Type your thoughts, commands, or 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        # Ingest thought and get agent response
        response, proposed_actions = agent.ingest_thought(user_input)
        print(f"Agent: {response}")

        # If agent has proposed actions, ask for approval
        if proposed_actions:
            print("\nAgent proposes:")
            for i, act in enumerate(proposed_actions):
                print(f"  [{i+1}] {act['description']}")
            approve = input("Approve actions? (y/n): ").strip().lower()
            if approve == 'y':
                exec_results = agent.execute_actions(proposed_actions)
                for res in exec_results:
                    print(f"Executed: {res}")
            else:
                print("Actions not executed.")

if __name__ == "__main__":
    main()
