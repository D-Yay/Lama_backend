import ollama
import psycopg2
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitted_text = []

with open('engineer of creativity.txt', 'r', encoding='utf-8') as text_file:
    raw_text_content = text_file.read()


    slicer = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50, separators= ['\n\n', '\n', ' '])
    splitted_text = slicer.split_text(raw_text_content)
    #now we got a list of string


connection = psycopg2.connect(
    host='db.tvohnpbfqfofsdhrukpq.supabase.co',
    #after the db to .co
    database='postgres',
    user='postgres',
    password='Tslb1112008!!',
    port='5432'
)

cursor = connection.cursor()

for chunk in splitted_text:
    embed_text = ollama.embeddings(model='nomic-embed-text', prompt=chunk)['embedding']
    cursor.execute('INSERT INTO document_chunk (doc_content, chunk_embedding) VALUES (%s, %s)', (str(chunk), str(embed_text)))
    connection.commit()

cursor.close()
connection.close()







