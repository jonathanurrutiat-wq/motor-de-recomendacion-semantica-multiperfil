def imprimir_separador1():
    print("\n" + "="*40)

def imprimir_separador2():
    print("\n" + "-"*40)

def mostrar_menu_principal():
    imprimir_separador1()
    print("MOTOR NEURO-SIMBÓLICO | PANEL CENTRAL")
    imprimir_separador2()

    print("1) Gestionar perfiles cinéfilos.")
    print("2) Ejecutar pipeline ETL (filtrar CSVs crudos).")
    print("3) Generar embeddings de un perfil.")
    print("4) Generar embeddings del lote de reseñas más reciente.")
    print("5) Cargar Ground-truth (dataset_maestro.csv).")
    print("6) Revisar películas pendientes de evaluar.")
    print("7) Entrenar modelo predictivo (Regresión Lineal).")
    print("8) Recomendar películas según el perfil.")
    print("9) Salir.")

    imprimir_separador2()


# ============ Menús de profiles.py ============

def mostrar_menu_perfiles():
    print("\n" + "="*35)
    print("Menú de gestión de perfiles cinéfilos")
    print("="*35)
    print("1. Crear/modificar un perfil")
    print("2. Mostrar perfiles existentes")
    print("3. Eliminar perfil existente")
    print("4. Volver al menú principal")
    print("="*35)

def menu_perfil_existente(nombre_perfil):
    print("\n" + "="*35)
    print(f"Menú de edición de perfil: {nombre_perfil}")
    print("="*35)
    print("1. Modificar nombre de perfil")
    print("2. Gestionar afinidades")
    print("3. Gestionar filtros restrictivos")
    print("4. Volver al menú principal")
    print("="*35)

def menu_afinidades(es_nuevo):
    print("\n" + "="*35)
    print("Menú de afinidades")
    print("="*35)
    print("1. Agregar/Modificar afinidad")
    print("2. Eliminar afinidad")
    if es_nuevo:
        print("3. Continuar a filtros restrictivos")
    else:
        print("3. Volver")
    print("="*35)

def menu_restrictivos():
    print("\n" + "="*35)
    print("Menú de filtros restrictivos")
    print("="*35)
    print("1. Agregar/Modificar filtro restrictivo")
    print("2. Eliminar filtro restrictivo")
    print("3. Volver")
    print("="*35)