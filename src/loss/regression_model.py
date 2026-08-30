import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

def main():
    root_dir = Path.cwd()
    loss_dir = root_dir / "src" / "loss"
    db_res_dir = root_dir / "src" / "db" / "filtered" / "result"
    
    # cargar el Ground Truth (matriz Y)
    gt_path = loss_dir / "matriz_perdida.csv"
    if not gt_path.exists():
        print("[!] Error: No se encontró matriz_perdida.csv. Ejecuta la Opción 4 primero.")
        return
    df_gt = pd.read_csv(gt_path)
    
    # buscar reseñas limpias (el contexto)
    archivos_csv = list(db_res_dir.glob("filtrado_*.csv"))
    if not archivos_csv:
        print("[!] Error: No hay CSVs filtrados. Ejecuta la Opción 2 primero.")
        return
    
    # tomar el archivo filtrado más reciente
    csv_reciente = max(archivos_csv, key=lambda p: p.stat().st_mtime)
    print(f"Vinculando contexto semántico desde: {csv_reciente.name}")
    df_reviews = pd.read_csv(csv_reciente)
    
    df_master = pd.merge(df_gt, df_reviews[['film_id', 'review_text']], on='film_id', how='inner')
    
    y = df_master['gt_nota_global'].fillna(0).values
    reviews_textos = df_master['review_text'].fillna("").tolist()
    
    # extraer descripciones de los filtros desde el Perfil
    perfiles_path = root_dir / "perfiles.json"
    with open(perfiles_path, 'r', encoding='utf-8') as f:
        perfiles_data = json.load(f)
        
    perfil_activo = next(iter(perfiles_data.values()))
    textos_filtros = []
    nombres_filtros = []
    
    for categoria in ['restrictivos', 'afinidad']:
        if categoria in perfil_activo:
            for nombre, datos in perfil_activo[categoria].items():
                textos_filtros.append(datos.get('descripcion_texto', ''))
                nombres_filtros.append(nombre)
                
    # embeddings y similitud del coseno
    print("\nCargando modelo neuronal de lenguaje...")
    modelo_nlp = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device="cuda")
    
    print("Vectorizando reseñas y filtros...")
    emb_reviews = modelo_nlp.encode(reviews_textos)
    emb_filtros = modelo_nlp.encode(textos_filtros)
    
    print("Calculando tensores de Similitud del Coseno (Matriz X)...")
    X = cosine_similarity(emb_reviews, emb_filtros)
    
    # entrenamiento del Perceptrón Base (regresión lineal múltiple)
    modelo = LinearRegression()
    modelo.fit(X, y)
    
    predicciones = modelo.predict(X)
    mse = mean_squared_error(y, predicciones)
    r2 = r2_score(y, predicciones)
    
    print("\n| -- Métricas Finales de Entrenamiento -- |")
    print(f"Películas evaluadas con éxito: {len(X)}")
    print(f"Error Cuadrático Medio (MSE): {mse:.4f}")
    print(f"Varianza Explicada (R^2): {r2:.4f}")
    
    print("\n| -- Pesos Sinápticos (Impacto semántico de cada filtro) -- |")
    for nombre, peso in zip(nombres_filtros, modelo.coef_):
        print(f" {nombre}: {peso:.4f}")
        
    print(f"\nSesgo Base (Nota promedio base de la red): {modelo.intercept_:.4f}")

if __name__ == '__main__':
    main()