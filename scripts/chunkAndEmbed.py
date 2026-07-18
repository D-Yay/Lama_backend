import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter


raw_text = 'this is my first time cooking a langchain text slicer'

text_slicer = RecursiveCharacterTextSplitter(chunk_size = 10, chunk_overlap = 6)

sliced_text = text_slicer.split_text(raw_text)

vector_response = ollama.embeddings(model='nomic-embed-text', prompt=sliced_text[0])


print(vector_response['embedding'])





