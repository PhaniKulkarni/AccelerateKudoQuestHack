"""
main.py - A simple interface to interact with the AIAgent.
"""

# Step 1: Import the necessary classes and modules
from agents.ai_agent import AIAgent

# Step 2: Define the main function
def main():
    # Step 3: Define a system message for the agent
    system_message = "You are an AI assistant. How can I help you today?"

    # Step 4: Define any tools the agent will use (customize as needed)
    tool_names = [
        "generate_suggestions",  # example tool
        "web_search_google",      # another example tool
        # Add more tools as necessary
    ]

    # Step 5: Initialize the AIAgent
    agent = AIAgent(system_message=system_message, tool_names=tool_names)

    print("Welcome to the AI Agent! Type 'exit' to end the conversation.")
    
    # Step 6: Start a loop to interact with the agent
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Exit condition
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        # Step 7: Run the agent and get a response
        response = agent.run(user_input)
        
        # Step 8: Print the agent's response
        print(f"AI: {response}")

# Step 9: Run the main function
if __name__ == "__main__":
    main()
