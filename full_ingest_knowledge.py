import ollama
from  langchain_text_splitters import RecursiveCharacterTextSplitter
import psycopg2
text_chunk = 'ur an expert document parser'

text_slicer= RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 1)
text_chunks = text_slicer.split_text(text_chunk)
#This returns a list of strings
#We often parse it in as 1 paragraph at a time, not 1 word at a time
#We should test the first element as a sample, like the pilot line production in business, then if it's alright we run a for loop to process the rest


vector_embedded_array = ollama.embeddings(model= 'nomic-embed-text', prompt=text_chunk)
vector_arrays = vector_embedded_array['embedding']



#now we establish the connection

#connection = psycopg2.connect('postgresql://postgres:Tslb1112008!!@db.tvohnpbfqfofsdhrukpq.supabase.co:5432/postgres')
connection = psycopg2.connect(
    host='db.tvohnpbfqfofsdhrukpq.supabase.co',
    database='postgres',
    user='postgres',
    password='Tslb1112008!!',
    port='5432'
)


cursor = connection.cursor()

cursor.execute('INSERT INTO document_chunk (doc_content, chunk_embedding) VALUES (%s,%s)', (text_chunk, str(vector_arrays)))

connection.commit()

cursor.close()
connection.close()










