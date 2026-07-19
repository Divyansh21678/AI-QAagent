from agents.qa_agent import QAAgent
from utils.report_generator import save_markdown

agent = QAAgent()

while True:
    print("\n==============================")
    print("      AI QA ENGINEER")
    print("==============================")
    print("1. Generate Functional Test Cases")
    print("2. Generate API Test Cases")
    print("3. Generate Security Test Cases")
    print("4. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":

        requirement = input("\nEnter Requirement:\n")

        response = agent.generate_functional_tests(requirement)

        print("\n")
        print(response)

        filename = requirement.lower().replace(" ", "_") + ".md"

        path = save_markdown(filename, response)

        print("\n====================================")
        print("✅ Report Saved Successfully")
        print(f"📄 File Location: {path}")
        print("====================================")

    elif choice == "2":

        requirement = input("\nEnter API Requirement:\n")

        response = agent.generate_api_tests(requirement)

        print("\n")
        print(response)

    elif choice == "3":

        requirement = input("\nEnter Security Requirement:\n")

        response = agent.generate_security_tests(requirement)

        print("\n")
        print(response)

    elif choice == "4":

        print("\n👋 Thank you for using AI QA Engineer.")
        break

    else:

        print("\n❌ Invalid Choice. Please try again.")