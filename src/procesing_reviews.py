import numpy as np
import pandas as pd
import semchunk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity  # Distnacia espacial coseno

from config import EMBEDDING_MODEL_NAME

#Expandir sentences trasnformwer a 512 tokens



def chunking_resenias(resenias:pd.DataFrame) -> list[dict]: 
    
    
    resenias_chunkeadas = [] # lista de diccionarios pelicula-reseña
    chunker = semchunk.chunkerify(EMBEDDING_MODEL_NAME, 128)
    
    for i in range(len(resenias)):
        
        texto_chunkeado = chunker(resenias.loc[i, "review_text"])
        resenias_chunkeadas.append({resenias.loc[i, "film_id"]: texto_chunkeado})
    
    return resenias_chunkeadas

def emdeings_resenias(resenias:list) -> list[dict]:
    embedings_resenias = []
    model = SentenceTransformer(EMBEDDING_MODEL_NAME, device = "cuda")
    temporal = []
    for i in range(len(resenias)):    
        for j, k in resenias[i].items(): # j es la clave, k es el valor
            ...
            
       
    return embedings_resenias


resenias = pd.read_csv(r"src\db\filtered\result\filtrado_2026-07-30_14-22-16.csv")



chunking_resenias(resenias)
