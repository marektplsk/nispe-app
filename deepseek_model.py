from langchain_ollama import OllamaLLM

# Initialize the DeepSeek model from Ollama
deepseek_model = OllamaLLM(model="deepseek-r1:1.5b")

# Function to generate a response with reasoning logs
def get_deepseek_response(prompt):
    try:
        print("\n🔍 Sending Prompt to DeepSeek Model:")
        print(prompt)  # Log the exact input sent

        # Stream the response to log the reasoning process
        response = ""
        for chunk in deepseek_model.stream(prompt):
            print(chunk, end="", flush=True)  # Show reasoning process in real-time
            response += chunk

        print("\n✅ Final Response Generated:\n", response)
        return response
    except Exception as e:
        print(f"❌ Error in get_deepseek_response: {e}")
        return "An error occurred while processing your request."


#fine tune 
#rozpoznat db symbols and from that make sure, aby ta ai mala knowledge co je co a aby to vedela rozoznat :D 
#fine tune it- make only one version of the model, so it will work, just as like as i desire ;D 
#knizxnice- dataset:emotions, fin BErt 
#kokot 



