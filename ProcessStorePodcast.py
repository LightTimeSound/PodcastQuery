from sentence_transformers import SentenceTransformer
import re
import faiss
import numpy as np
from Podcast import Podcast
import pickle
import yaml
import os
from DatabaseManager import DatabaseManager
from sys import exit

def main():
    model_name = 'sentence-transformers/all-mpnet-base-v2'
    podcast_name = 'Flirting With Models'
    psp = ProcessStorePodcast(model=model_name, podcast_name=podcast_name)
    psp.main()


class ProcessStorePodcast:
    def __init__(self, model, podcast_name):
        self.model = SentenceTransformer(model)
        self.dbm = DatabaseManager()
        self.podcast_name = podcast_name
        
        with open("config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)
            
        self.index_path = config["index_path"]
        self.metadata_path = config["metadata_path"]
        
        
    def main(self):
        podcasts = Podcast.get_podcast_from_db(self.dbm, self.podcast_name)
        
        cleaned_podcasts, paragraphs_per_podcast = self.preprocess_podcasts(podcasts)
    
        transcript_vectors = self.encode_podcasts(self.model, cleaned_podcasts)
        
        vector_dim = transcript_vectors.shape[1]
        index = self.create_faiss_index(vector_dim)
        
        # If the index exists, get the maximum id and start from the next one
        if os.path.exists(self.index_path):
            max_id = faiss.read_index(self.index_path).ntotal
        else:
            max_id = -1
        
        # Generate new ids starting from max_id + 1
        ids = list(range(max_id + 1, max_id + 1 + len(cleaned_podcasts)))
        
        # Update the index with new vectors and ids
        self.update_faiss_index(index, transcript_vectors, self.index_path, ids)
        
        metadata = self.store_podcasts_in_database(index, transcript_vectors, cleaned_podcasts, ids, paragraphs_per_podcast)
        self.update_metadata(metadata, self.metadata_path)
    
    def segment_transcript(self, transcript):
        # Split the transcript into sentences or chunks
        # Here we use a simple approach by splitting on periods.
        # More sophisticated segmentation can be done using NLP libraries like spaCy or NLTK.
        paragraphs = transcript.split('\n\n')  # Assuming two newlines separate paragraphs
        segments = []
        for paragraph_index, paragraph in enumerate(paragraphs):
            # Further split each paragraph into sentences
            sentences = paragraph.split('. ')
            for sentence_index, sentence in enumerate(sentences):
                segments.append((sentence, paragraph_index, sentence_index))
        return segments, paragraphs
        
    def preprocess_transcript(self, transcript):
        transcript = transcript.lower()
        cleaned_transcript = re.sub(r'[^a-zA-Z0-9\s]', '', transcript)
        return cleaned_transcript

    def preprocess_podcasts(self, podcasts):
        cleaned_podcasts = []
        paragraphs_per_podcast = {}
        for podcast in podcasts:
            cleaned_transcript = self.preprocess_transcript(podcast.transcript)
            segments, paragraphs = self.segment_transcript(cleaned_transcript)
            paragraphs_per_podcast[podcast.title] = paragraphs
            for segment, paragraph_index, _ in segments:
                cleaned_podcasts.append((podcast.title, podcast.url, segment, paragraph_index))
        return cleaned_podcasts, paragraphs_per_podcast

    def encode_podcasts(self, model, podcast_segments):
        # Extract just the segments for encoding
        transcripts = [segment for title, url, segment, paragraph_index, *_ in podcast_segments]
        transcript_vectors = model.encode(transcripts, convert_to_tensor=True)
        return transcript_vectors.cpu().numpy()

    def store_podcasts_in_database(self, index, transcript_vectors, podcast_segments, ids, paragraphs_per_podcast):
        self.store_vectors_in_database(index, transcript_vectors, ids)
        metadata = {id: {'title': title, 'url': url, 'segment': segment, 'paragraph_index': paragraph_index, 'paragraph': paragraphs_per_podcast[title][paragraph_index]}
                    for id, (title, url, segment, paragraph_index) in zip(ids, podcast_segments)}
        return metadata

    def create_faiss_index(self, vector_dim):
        index = faiss.IndexFlatL2(vector_dim)  # Create a flat (brute-force) L2 index
        index = faiss.IndexIDMap(index)        # Wrap the index with IndexIDMap to support add_with_ids
        return index
    
    def update_faiss_index(self, index, new_vectors, index_path, ids):
        if os.path.exists(index_path):
            index = faiss.read_index(index_path)
            if not isinstance(index, faiss.IndexIDMap):
                index = faiss.IndexIDMap(index)
        else:
            vector_dim = new_vectors.shape[1]
            index = self.create_faiss_index(vector_dim)

        index.add_with_ids(new_vectors, np.array(ids).astype('int64'))
        faiss.write_index(index, index_path)
            
    def update_metadata(self, new_metadata, metadata_path):
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
        else:
            metadata = {}

        metadata.update(new_metadata)

        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)

    def store_vectors_in_database(self, index, transcript_vectors, ids):
        transcript_vectors = np.array(transcript_vectors).astype('float32')
        index.add_with_ids(transcript_vectors, np.array(ids).astype('int64'))
        
    def delete_podcasts_from_database(self, ids_to_delete):
        # Load the existing FAISS index
        if os.path.exists(self.index_path):
            index = faiss.read_index(self.index_path)
        else:
            raise FileNotFoundError(f"FAISS index file not found at {self.index_path}")

        # Remove the vectors with the specified IDs from the index
        faiss_ids_to_delete = np.array(ids_to_delete).astype('int64')
        index.remove_ids(faiss_ids_to_delete)

        # Write the updated index back to the file
        faiss.write_index(index, self.index_path)

        # Load the existing metadata
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'rb') as f:
                metadata = pickle.load(f)
        else:
            raise FileNotFoundError(f"Metadata file not found at {self.metadata_path}")

        # Remove the metadata entries with the specified IDs
        for id_to_delete in ids_to_delete:
            metadata.pop(id_to_delete, None)

        # Write the updated metadata back to the file
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
    
if __name__ == "__main__":
    main()