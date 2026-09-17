import pandas as pd
import numpy as np
from pathlib import Path
import chromadb
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics.pairwise import cosine_similarity
from src.normalizacion import (
    cargar_perfil_actual,
    canonicalizar_film_id,
    nombre_columna_gt,
    obtener_filtros_del_perfil,
)

def main():
    rootDirectory = Path.cwd()
    chromaDirectory = rootDirectory / "src" / "db" / "embeddings" / "chroma"
    lossDirectory = rootDirectory / "src" / "loss"
    gtPath = lossDirectory / "matriz_perdida.csv"

    if not gtPath.exists():
        print("[!] Error: No se encontró matriz_perdida.csv. Ejecuta el módulo 5 primero.")
        return

    print("Conectando con la base de datos vectorial ChromaDB...")
    chromaClient = chromadb.PersistentClient(path=str(chromaDirectory))
    
    collectionProfiles = chromaClient.get_collection(name="perfiles")
    collectionReviews = chromaClient.get_collection(name="resenias") 

    # extracción de tensores
    profileData = collectionProfiles.get(include=['embeddings', 'metadatas'])
    
    # Se arma dinámicamente a partir del perfil activo en perfiles.json:
    # si se agrega un perfil nuevo o se le cambian los filtros a uno
    # existente, esto se actualiza solo (ver src/normalizacion.py).
    perfilActual = cargar_perfil_actual()
    filtrosPerfil = obtener_filtros_del_perfil(perfilActual)

    orderedFilterNames = [nombre for _, nombre in filtrosPerfil]
    orderedColumns = [nombre_columna_gt(tipo, nombre) for tipo, nombre in filtrosPerfil]
    
    embFiltersList = []
    for filterName in orderedFilterNames:
        filterIndex = None
        for i, meta in enumerate(profileData['metadatas']):
            if meta['filtro'] == filterName:
                filterIndex = i
                break
        
        if filterIndex is not None:
            embFiltersList.append(profileData['embeddings'][filterIndex])
        else:
            # vector nulo (ortogonal) si el filtro fue eliminado del perfil
            embFiltersList.append([0.0] * 384)
            
    embFilters = np.array(embFiltersList)

    # extracción de tensores de reseñas y cruce con el ground truth
    reviewsData = collectionReviews.get(include=['embeddings'])
    reviewIds = reviewsData['ids']
    reviewEmbeddings = reviewsData['embeddings']
    
    # diccionario para acceso O(1) usando ID canonicalizado
    reviewsDict = {canonicalizar_film_id(reviewIds[i]): reviewEmbeddings[i] for i in range(len(reviewIds))}
    
    dfGt = pd.read_csv(gtPath)
    dfGt['canon_id'] = dfGt['film_id'].apply(canonicalizar_film_id)
    
    matchedEmbeddings = []
    matchedY = []
    
    for _, row in dfGt.iterrows():
        canonId = row['canon_id']
        if canonId in reviewsDict:
            matchedEmbeddings.append(reviewsDict[canonId])
            matchedY.append(row['gt_nota_global'])
            
    if not matchedY:
        print("[!] Error: No se lograron cruzar las reseñas vectorizadas con el Ground Truth.")
        return
        
    embReviews = np.array(matchedEmbeddings)
    yArray = np.array(matchedY)

    # cálculo de la Similitud del Coseno (Matriz X)
    print("Calculando distancias semánticas (Matriz X)...")
    matrixX = cosine_similarity(embReviews, embFilters)

    # entrenamiento perceptrón base
    print("Entrenando Regresión Lineal...")
    linearModel = LinearRegression()
    linearModel.fit(matrixX, yArray)
    
    predictions = linearModel.predict(matrixX)
    mseValue = mean_squared_error(yArray, predictions)
    r2Value = r2_score(yArray, predictions)
    
    # Reporte
    print("\n| -- Métricas Finales de Entrenamiento -- |")
    print(f"Películas evaluadas con éxito (Cruce Vectorial): {len(matrixX)}")
    print(f"Error Cuadrático Medio (MSE): {mseValue:.4f}")
    print(f"Varianza Explicada (R^2): {r2Value:.4f}")
    
    print("\n| -- Pesos Sinápticos (Impacto semántico de cada filtro) -- |")
    for colName, weight in zip(orderedColumns, linearModel.coef_):
        print(f" {colName}: {weight:.4f}")
        
    print(f"\nSesgo Base (Bias): {linearModel.intercept_:.4f}")

if __name__ == '__main__':
    main()