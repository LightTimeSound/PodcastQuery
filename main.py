from sentence_transformers import SentenceTransformer
from LLMClient import LLMClient
from Podcast import Podcast
import faiss
import pickle
import yaml

model_name = 'sentence-transformers/all-mpnet-base-v2'
local_llm_client = LLMClient('http://localhost:1234/v1')
query = 'I want to create my first model for trading at home to have passive income'

def main():
    model = SentenceTransformer(model_name)
    
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
            
    index_path = config["index_path"]
    metadata_path = config["metadata_path"]
    
    index = load_faiss_index(index_path)
    metadata = load_metadata(metadata_path)
    
    query_vector = generate_query_vector(model, query)
    
    # Retrieve and summarize similar podcasts
    similar_podcasts = retrieve_similar_podcasts(index, metadata, query_vector)
    summaries = summarize_podcasts(local_llm_client, similar_podcasts)
    
    # Print or process the summaries along with metadata
    for summary in summaries:
        print(f"Title: {summary['title']}")
        print(f"URL: {summary['url']}")
        print(f"Summary: {summary['summary']}\n")

def load_faiss_index(index_path):
    return faiss.read_index(index_path)

def load_metadata(metadata_path):
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)
    return metadata


# Step 4: Querying with an LLM
def generate_query_vector(model, query):
    query_vector = model.encode([query], convert_to_tensor=True)
    return query_vector.cpu().numpy()  # Convert tensor to numpy array if needed

# Step 5: Retrieving Relevant Information
def retrieve_similar_podcasts(index, metadata, query_vector, top_k=5):
    distances, indices = index.search(query_vector, top_k)
    # Filter out any indices that are -1
    valid_indices = [idx for idx in indices[0] if idx != -1]
    similar_podcasts = []
    for id in valid_indices:
        data = metadata[id]
        similar_podcasts.append({
            'title': data['title'],
            'url': data['url'],
            'segment': data['segment'],
            'paragraph': data['paragraph']  # Retrieve the full paragraph for context
        })
    return similar_podcasts

# Step 6: Summarization
def summarize_podcasts(local_llm_client, similar_podcasts):
    summaries = []
    for podcast_metadata in similar_podcasts:
        summary = local_llm_client.summarize(podcast_metadata['paragraph'])  # Assuming 'transcript' is part of the metadata
        summaries.append({
            'title': podcast_metadata['title'],
            'url': podcast_metadata['url'],
            'summary': summary
        })
    return summaries

if __name__ == '__main__':
    main()