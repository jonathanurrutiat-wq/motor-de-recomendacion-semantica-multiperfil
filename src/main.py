import sys
from pathlib import Path

curr_dir = Path(__file__).resolve().parent
sys.path.append(str(curr_dir))
sys.path.append(str(curr_dir.parent))

# ============ Importaciones ============
import profiles as prfs
import src.procesing_profiles as emb_perfiles
import src.procesing_reviews as emb_resenias
import visuals as vis
from src.db.filtered.filter import main as run_filter
from src.loss.gt_matrix_pipeline import main as run_pipeline
from src.loss.ingest_maestro import main as run_maestro


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
                run_filter()

            case "3":
                nombre_perfil = input("Ingrese el nombre del perfil a embeddear: ").strip().title()
                print(f"\n[3] Generando embeddings para el perfil '{nombre_perfil}'...")
                emb_perfiles.main(nombre_perfil)

            case "4":
                print("\n[4] Generando embeddings del lote de reseñas más reciente...")
                emb_resenias.main()

            case "5":
                print("\n[5] Cargando Ground-truth (dataset_maestro.csv)...")
                run_maestro()

            case "6":
                print("\n[6] Revisando películas pendientes de evaluar...")
                run_pipeline()

            case "7":
                print("Saliendo del panel central.")
                sys.exit(0)

            case _:
                print("Opción no válida. Por favor, seleccione una opción del 1 al 7.")


if __name__ == '__main__':
    main()