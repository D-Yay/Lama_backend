from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2, ollama
from fastapi.middleware.cors import CORSMiddleware

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
    vectorized_array = ollama.embeddings(model='nomic-embed-text', prompt=question_payload.user_question)
    vectorized_question = vectorized_array['embedding']

    connection = psycopg2.connect(
        host='db.tvohnpbfqfofsdhrukpq.supabase.co',
        #after the db to .co
        database='postgres',
        user='postgres',
        password='Tslb1112008!!',
        port='5432'

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


    AI_response = ollama.chat(model='llama3', messages= [{'role':'system', 'content': system_prompt}, {'role':'user', 'content':augmented_prompt}])
    AI_text_response = AI_response['message']['content']

    return {'status' : 'success', 'answer':AI_text_response}













