from langchain_ollama import OllamaLLM

mistral_model = OllamaLLM(model="mistral")

def get_mistral_response(prompt):
    try:
        response = mistral_model(prompt)
        return response
    except Exception as e:
        print(f"Error in get_mistral_response: {e}")
        return "An error occurred while processing your request."
