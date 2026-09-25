import sys
from pathlib import Path

currDir = Path(__file__).resolve().parent
sys.path.append(str(currDir))
sys.path.append(str(currDir.parent))

# ============ Importaciones ============
import profiles as prfs
import src.procesing_profiles as embPerfiles
import src.procesing_reviews as embResenias
import visuals as vis
from src.analisis import main as runAnalisis
from src.db.filtered.filter import main as runFilter
from src.loss.gt_matrix_pipeline import main as runPipeline
from src.loss.ingest_maestro import main as runMaestro
from src.recommend import main as runRecommend
from src.scoring import main as runScoring


def main():
    while True:
        vis.mostrar_menu_principal()
        opcion = input("Seleccione su módulo a ejecutar\n< ")

        match opcion:
            case "1":
                print("\n[1] Gestionando perfiles cinéfilos...")
                prfs.main()

            case "2":
                print("\n[2] Ejecutando pipeline ETL (filtrando CSVs crudos)...")
                runFilter()

            case "3":
                print(f"\n[3] Generando embeddings para el perfil...")
                embPerfiles.main()

            case "4":
                print("\n[4] Generando embeddings de los lotes de reseñas pendientes...")
                embResenias.main()

            case "5":
                print("\n[5] Cargando Ground-truth (dataset_maestro.csv)...")
                runMaestro()

            case "6":
                print("\n[6] Revisando películas pendientes de evaluar...")
                runPipeline()

            case "7":
                print("\n[7] Entrenando modelo predictivo (Regresión lineal)...")
                runScoring()

            case "8":
                print("\n[8] Generando ranking de recomendaciones...")
                runRecommend()

            case "9":
                print("\n[9] Ejecutando todo el pipeline y generando datos de análisis...")
                runAnalisis()

            case "10":
                print("Saliendo del panel central.")
                sys.exit(0)

            case _:
                print("Opción no válida. Por favor, seleccione una opción del 1 al 10.")

if __name__ == '__main__':
    main()