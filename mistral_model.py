from langchain_ollama import OllamaLLM

# Initialize the Mistral model from Ollama
mistral_model = OllamaLLM(model="mistral")

# Define a function to get the response from Mistral
def get_mistral_response(prompt):
    try:
        response = mistral_model(prompt)
        return response
    except Exception as e:
        print(f"Error in get_mistral_response: {e}")
        return "An error occurred while processing your request."


#fine tune 
#rozpoznat db symbols and from that make sure, aby ta ai mala knowledge co je co a aby to vedela rozoznat :D 
#fine tune it- make only one version of the model, so it will work, just as like as i desire ;D 
#knizxnice- dataset:emotions, fin BErt 
#kokot 



Google Colab Subscription	Predplatné	12	15	180
Figma Subscription	Predplatné	12	12	144
Adobe Pack Subscription	Predplatné	12	60	720
Social Analytics Tool	Predplatné	12	50	600
Microsoft Pack (Excel, Word)	Predplatné	12	30	360
Notion Subscription	Predplatné	12	10	120
App Development Tools	Predplatné	12	100	1 200
Server Hosting	Prevádzkové náklady	12	200	2 400
Priestory (prenájom)	Prevádzkové náklady	12	1 000	12 000
Rekonštrukcia priestorov	Jednorazový náklad	1	8 000	8 000
Auto na služobné účely	Investícia	1	15 000	15 000
Hardware (laptop, PC)	Investícia	3	1 500	4 500
Marketing	Prevádzkové náklady	1	2 000	2 000
Licencie a certifikáty	Jednorazový náklad	1	1 200	1 200
Vývoj aplikácie (outsourcing)	Jednorazový náklad	1	3 500	3 500
Testing a QA nástroje	Jednorazový náklad	1	600	600
Celkové náklady				50 524
