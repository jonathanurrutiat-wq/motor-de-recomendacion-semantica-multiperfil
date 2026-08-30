import sys
import os
from pathlib import Path

curr_dir = Path(__file__).resolve().parent
sys.path.append(str(curr_dir))
sys.path.append(str(curr_dir.parent))

# ============ Importaciones proyectadas ============
from src.db.filtered.filter import main as run_filter
from src.loss.gt_matrix_pipeline import main as run_pipeline
from src.loss.ingest_maestro import main as run_maestro
from src.loss.regression_model import main as run_regression # <-- importación más reciente
import src.embeddings as emb
import profiles as prfs

def imprimir_separador1():
    print("\n" + "="*40)

def imprimir_separador2():
    print("\n" + "-"*40)

def mostrar_menu_principal():
    imprimir_separador1()
    print("MOTOR NEURO-SIMBÓLICO | PANEL CENTRAL")
    imprimir_separador2()

    print("1) Gestionar perfiles cinéfilos (Front-end).")
    print("2) Ejecutar pipeline ETL (Filtrar CSVs crudos).")
    print("3) Generar embeddings del perfil activo.")
    print("4) Cargar Ground-truth (CSV_100_peliculas)")
    print("5) Entrenar modelo predictivo (Regresión lineal)")
    print("6) Salir.")

    imprimir_separador2()

def main():
    while True:
        mostrar_menu_principal()
        opcion = input("Seleccione su módulo a ejecutar\n< ")

        match opcion:
            case "1":
                prfs.main()
            case "2":
                run_filter()
            case "3":
                emb.main()
            case "4":
                run_maestro()
                print("Test módulo 4 finalizado.")
            case "5":
                run_regression()
                print("Entrenamiento finalizado.")
            case "6":
                sys.exit(0)

if __name__ == '__main__':
    main()