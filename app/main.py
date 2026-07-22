from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2, ollama
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from config import env_config
from groq import Groq
import requests


supabase_password = env_config.PASSWORD
grog_api_key = env_config.GROQ_API_KEY
client = Groq(api_key= grog_api_key)
nomic_api_key = env_config.NOMIC_API_KEY
current_environemnt = env_config.ENVIRONMENT

#pydantic firewall, will return error if data doesnt match type hint
class requestInput(BaseModel):
    user_question : str


app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins = ['*'],
	#Type our specific URL here, * means everything is accepted
	
	allow_credentials = True,
	allow_methods = ['*'],
	allow_headers = ['*'],
)


@app.post('/prompt')
#turn on the chef waiting for uvicorn request then pass the ticket to the cooking station below

async def ask_AI(question_payload: requestInput):
    vectorized_array = []
    
    if current_environemnt == 'development':
        vectorized_array = ollama.embeddings(model='nomic-embed-text', prompt=question_payload.user_question)
        vectorized_question = vectorized_array['embedding']

    else:
        # 1. Setup the Network Target
        nomic_cloud_url = "https://api-atlas.nomic.ai/v1/embedding/text"

        # 2. Attach your VIP pass
        nomic_headers = {
            "Authorization": f"Bearer {nomic_api_key}"
        }

        # 3. Package the payload (Must match the Nomic schema)
        nomic_payload = {
            "model": "nomic-embed-text-v1.5", # The cloud version of your local model
            "texts": [question_payload.user_question],  # The API requires a LIST of strings
            "task_type": "search_query"       # Tells Nomic this is for RAG
        }

        # 4. Shoot to Cloud and Extract
        cloud_response = requests.post(nomic_cloud_url, headers=nomic_headers, json=nomic_payload)
        vectorized_question = cloud_response.json()['embeddings'][0]


    connection = psycopg2.connect(
        host='aws-1-ap-southeast-1.pooler.supabase.com',
        port = '6543',
        database = 'postgres',
        user = 'postgres.tvohnpbfqfofsdhrukpq',
        password = supabase_password
    )

    cursor = connection.cursor()

    cursor.execute('SELECT doc_content FROM document_chunk ORDER BY chunk_embedding <=> %s LIMIT 1', (str(vectorized_question),))
    best_match = cursor.fetchone()[0]

    cursor.close()
    connection.close()


    augmented_prompt = f'''

    context: {best_match}
    question: {question_payload.user_question}

    '''

    system_prompt = '''

    You are a deterministic data extraction engine. 

    EXECUTION RULES:
    1. You must analyze the User's Question and the Provided Context.
    2. If the context does NOT explicitly contain the specific facts needed to answer the entire question, you must instantly abort and output EXACTLY: "data not found".
    3. Do not assume, guess, or use outside knowledge. 
    4. Do not compare items unless the comparison is explicitly written in the context.

    VIOLATING THESE RULES RESULTS IN SYSTEM FAILURE.

    '''

    AI_text_response = ''
   

    if current_environemnt == 'development':
        #we use ollama to run llama3 locally

        AI_response = ollama.chat(model='llama3', messages= [{'role':'system', 'content': system_prompt}, {'role':'user', 'content':augmented_prompt}])
        AI_text_response = AI_response['message']['content']
    else:
        #we send a request to Grog to run on cloud

        AI_response = client.chat.completions.create(
            model='llama3-8b-8192',
            messages=[{'role':'system', 'content':system_prompt}, {'role':'user', 'content': augmented_prompt}]
        )
        AI_text_response = AI_response.choices[0].message.content


    return {'status' : 'success', 'answer':AI_text_response}












#test auto deploy
