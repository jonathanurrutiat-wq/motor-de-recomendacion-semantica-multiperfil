import numpy as np
import pandas as pd
import semchunk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity  # Distnacia espacial coseno

from config import EMBEDDING_MODEL_NAME

#Expandir sentences trasnformwer a 512 tokens



def chunking_resenias(resenias:pd.DataFrame) -> dict[str,str]: #la key tiene que ser el title id + un identificador unico
    
    
    resenias_chunkeadas = {}
    chunker = semchunk.chunkerify(EMBEDDING_MODEL_NAME, 128)
    
    for i in range(0,len(resenias)):
        
        texto_chunkeado = chunker(resenias.loc[i, "review_text"])
    
    return resenias_chunkeadas




resenias = pd.read_csv(r"src\db\filtered\result\filtrado_2026-07-30_14-22-16.csv")



