import json
import os

archivo_perfiles = "perfiles.json"

if os.path.exists(archivo_perfiles):
    with open(archivo_perfiles, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
else:
    datos = {}

def mostrar_menu():
    print("\n" + "="*35)
    print("Menú de creación y visualización de perfiles")
    print("="*35)
    print("1. Crear/actualizar perfil")
    print("2. Mostrar perfiles existentes")
    print("3. Eliminar un perfil")
    print("4. Salir")
    print("="*35)

def menu_perfil_existente():
    print("\n" + "="*35)
    print("Menú de edición de perfil")
    print("="*35)
    print("1. Modificar nombre de perfil")
    print("2. Gestionar afinidades")
    print("3. Gestionar filtros restrictivos")
    print("4. Volver al menú principal")
    print("="*35)

def menu_afinidades():
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

def gestionar_afinidades(nombre_perfil):
    while True:
        menu_afinidades()
        opcion_afinidad = input("Seleccione una opción: ")
        
        if opcion_afinidad == "1":
            afinidad = input("Ingrese la afinidad a agregar/modificar: ")
            if afinidad in datos[nombre_perfil]["afinidad"]:
                modificar = input(f"La afinidad '{afinidad}' ya existe. ¿Desea modificarla? (s/n): ")
                if modificar.lower() == "s":
                    nueva_afinidad = input("Ingrese la nueva afinidad (o deje en blanco si la quiere mantener): ")
                    if nueva_afinidad:
                        datos[nombre_perfil]["afinidad"][nueva_afinidad] = datos[nombre_perfil]["afinidad"].pop(afinidad)
                        afinidad = nueva_afinidad
                    else:
                        print("No se realizaron cambios en la afinidad.")
                        continue
                else:
                    print("No se realizaron cambios en la afinidad.")
                    continue
            else:
                print(f"Agregando una nueva afinidad: '{afinidad}'")
                datos[nombre_perfil]["afinidad"][afinidad] = {}
            
            descripcion_afinidad = input("Ingrese la descripción de la afinidad: ")
            
            importancia_base = float(input("Ingrese la importancia base de la afinidad (1-10): "))
            while not (1 <= importancia_base <= 10):
                importancia_base = float(input("Por favor, ingrese un número válido entre 1 y 10 para la importancia base: "))
            
            datos[nombre_perfil]["afinidad"][afinidad] = {
                "descripcion": descripcion_afinidad,
                "importancia_base": float(importancia_base)
            }
            print("Afinidad agregada/modificada exitosamente.")
        
        elif opcion_afinidad == "2":
            afinidad_eliminar = input("Ingrese la afinidad a eliminar: ")
            if afinidad_eliminar in datos[nombre_perfil]["afinidad"]:
                confirmar = input(f"¿Está seguro de que desea eliminar la afinidad '{afinidad_eliminar}'? (s/n): ")
                if confirmar.lower() == "s":
                    del datos[nombre_perfil]["afinidad"][afinidad_eliminar]
                    print(f"Afinidad '{afinidad_eliminar}' eliminada exitosamente.")
                else:
                    print("Eliminación cancelada.")
            else:
                print(f"No se encontró la afinidad '{afinidad_eliminar}'.")
        
        elif opcion_afinidad == "3":
            if es_nuevo and not datos[nombre_perfil]["afinidad"]:
                confirmar_vacio = input("Este perfil no tiene ninguna afinidad registrada. ¿Desea continuar de todas formas? (s/n): ")
                if confirmar_vacio.lower() != "s":
                    continue
            break
        
        else:
            print("Opción no válida.")

def gestionar_restrictivos(nombre_perfil):
    while True:
        menu_restrictivos()
        opcion_restrictivo = input("Seleccione una opción: ")
        
        if opcion_restrictivo == "1":
            filtro = input("Ingrese el filtro restrictivo a agregar/modificar: ")
            if filtro in datos[nombre_perfil]["restrictivos"]:
                modificar = input(f"El filtro '{filtro}' ya existe. ¿Desea modificarlo? (s/n): ")
                if modificar.lower() == "s":
                    nuevo_filtro = input("Ingrese el nuevo filtro restrictivo (o deje en blanco si lo quiere mantener): ")
                    if nuevo_filtro:
                        datos[nombre_perfil]["restrictivos"][nuevo_filtro] = datos[nombre_perfil]["restrictivos"].pop(filtro)
                        filtro = nuevo_filtro
                    else:
                        print("No se realizaron cambios en el filtro.")
                        continue
                else:
                    print("No se realizaron cambios en el filtro.")
                    continue
            else:
                print(f"Agregando un nuevo filtro restrictivo: '{filtro}'")
                datos[nombre_perfil]["restrictivos"][filtro] = {}
            
            desc_texto = input("Ingrese la descripción del filtro: ")
            severidad = None
            while (severidad not in ["veto absoluto", "grave", "moderada a grave", "moderada", "leve"]):
                severidad = input("Ingrese la severidad del filtro (veto absoluto/grave/moderada a grave/moderada/leve): ").lower()
                if severidad == "veto absoluto":
                    nivel = "3"
                elif severidad == "grave":
                    nivel = "2.5"
                elif severidad == "moderada a grave":
                    nivel = "2"
                elif severidad == "moderada":
                    nivel = "1.5"
                elif severidad == "leve":
                    nivel = "1"
                else:
                    print("Severidad no válida. Por favor, ingrese una de las opciones válidas.")
            
            afinidades_existentes = list(datos[nombre_perfil]["afinidad"].keys())
            if afinidades_existentes:
                print(f"Afinidades registradas en este perfil: {', '.join(afinidades_existentes)}")
            else:
                print("Este perfil no tiene afinidades registradas.")
            
            corrupcion_directa = []
            while True:
                corrupcion_input = input("Ingrese las afinidades que corrompe este filtro, separadas por coma (si no hay, deje en blanco): ")
                if not corrupcion_input.strip():
                    corrupcion_directa = []
                    break
                
                nombres_ingresados = [c.strip() for c in corrupcion_input.split(",") if c.strip()]
                no_encontrados = [n for n in nombres_ingresados if n not in afinidades_existentes]
                
                if no_encontrados:
                    print(f"Aviso: las siguientes afinidades no existen en este perfil: {', '.join(no_encontrados)}")
                    decision = input("¿Desea (g)uardarlas igual, (c)orregir, o (v)aciar la lista? (g/c/v): ").lower()
                    if decision == "g":
                        corrupcion_directa = nombres_ingresados
                        break
                    elif decision == "v":
                        corrupcion_directa = []
                        break
                    else:
                        continue
                else:
                    corrupcion_directa = nombres_ingresados
                    break
            
            excepcion = input("Ingrese la excepcion del filtro (si no hay, deje en blanco): ") or None
            datos[nombre_perfil]["restrictivos"][filtro] = {
                "descripcion_texto": desc_texto,
                "nivel": nivel,
                "severidad": severidad,
                "corrupcion_directa": corrupcion_directa,
                "excepcion_texto": excepcion
            }
            print("Filtro agregado/modificado exitosamente.")
        
        elif opcion_restrictivo == "2":
            filtro_eliminar = input("Ingrese el filtro restrictivo a eliminar: ")
            if filtro_eliminar in datos[nombre_perfil]["restrictivos"]:
                confirmar = input(f"¿Está seguro de que desea eliminar el filtro '{filtro_eliminar}'? (s/n): ")
                if confirmar.lower() == "s":
                    del datos[nombre_perfil]["restrictivos"][filtro_eliminar]
                    print(f"Filtro '{filtro_eliminar}' eliminado exitosamente.")
                else:
                    print("Eliminación cancelada.")
            else:
                print(f"No se encontró el filtro '{filtro_eliminar}'.")
        
        elif opcion_restrictivo == "3":
            break
        
        else:
            print("Opción no válida.")

while True:
    mostrar_menu()
    opcion = input("Seleccione una opción: ")
    
    if opcion == "1":
        nombre_perfil = input("\nIngrese un nombre de perfil: ")
        nombre_perfil = nombre_perfil.strip()
        nombre_perfil = nombre_perfil.title() 
        
        es_nuevo = nombre_perfil not in datos
        
        if not es_nuevo:
            eleccion = input(f"El perfil '{nombre_perfil}' ya existe. ¿Desea modificarlo? (s/n): ")
            if eleccion.lower() != "s":
                print("No se realizaron cambios en el perfil.")
                continue
        else:
            print(f"Creando un nuevo perfil: '{nombre_perfil}'")
            datos[nombre_perfil] = {"restrictivos": {}}
            datos[nombre_perfil] = {"afinidad": {}}
        
        if "restrictivos" not in datos[nombre_perfil]:
            datos[nombre_perfil]["restrictivos"] = {}
        if "afinidad" not in datos[nombre_perfil]:
            datos[nombre_perfil]["afinidad"] = {}
        
        if es_nuevo:
            # Flujo forzado: primero afinidades, después restrictivos
            gestionar_afinidades(nombre_perfil)
            gestionar_restrictivos(nombre_perfil)
        else:
            # Perfil existente: acceso libre a cualquier sección
            while True:
                menu_perfil_existente()
                opcion_edicion = input("Seleccione una opción: ")
                
                if opcion_edicion == "1":
                    nuevo_nombre = input("Ingrese el nuevo nombre del perfil: ")
                    if nuevo_nombre and nuevo_nombre != nombre_perfil:
                        datos[nuevo_nombre] = datos.pop(nombre_perfil)
                        print(f"El perfil ha sido renombrado a '{nuevo_nombre}'.")
                        nombre_perfil = nuevo_nombre
                    else:
                        print("Nombre no válido o igual al anterior. No se realizaron cambios.")
                
                elif opcion_edicion == "2":
                    gestionar_afinidades(nombre_perfil)
                
                elif opcion_edicion == "3":
                    gestionar_restrictivos(nombre_perfil)
                
                elif opcion_edicion == "4":
                    print("Volviendo al menú principal.")
                    break
                
                else:
                    print("Opción no válida.")

    elif opcion == "2":
        if not datos:
            print("No hay perfiles existentes.")
        else:
            print("\nPerfiles existentes:")
            for perfil, contenido in datos.items():
                print(f"\nPerfil: {perfil}")
                for filtro, detalles in contenido["restrictivos"].items():
                    print(f"  Filtro: {filtro}")
                    print(f"    Descripción: {detalles['descripcion_texto']}")
                    print(f"    Severidad: {detalles['severidad']}")
                    print(f"    Nivel: {detalles['nivel']}")
                    corrupcion = detalles.get('corrupcion_directa', [])
                    print(f"    Corrupción directa: {', '.join(corrupcion) if corrupcion else 'Ninguna'}")
                    excepcion = detalles.get('excepcion_texto', 'Ninguna')
                    print(f"    Excepción: {excepcion}")
                for afinidad, detalles in contenido["afinidad"].items():
                    print(f"  Afinidad: {afinidad}")
                    print(f"    Descripción: {detalles['descripcion']}")
                    print(f"    Importancia Base: {detalles['importancia_base']}")

    elif opcion == "3":
        nombre_perfil = input("Ingrese el nombre del perfil a eliminar: ")
        nombre_perfil = nombre_perfil.strip()
        nombre_perfil = nombre_perfil.title() 
        if nombre_perfil in datos:
            confirmar = input(f"¿Está seguro de que desea eliminar el perfil '{nombre_perfil}'? (s/n): ")
            if confirmar.lower() == "s":
                del datos[nombre_perfil]
                print(f"Perfil '{nombre_perfil}' eliminado exitosamente.")
            else:
                print("Eliminación cancelada.")
        else:
            print(f"No se encontró el perfil '{nombre_perfil}'.")
    
    elif opcion == "4":
        with open(archivo_perfiles, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
        print("Datos guardados. Saliendo del menú de perfiles.")
        break
    
    else:
        print("Opción no válida. Por favor, seleccione una opción del 1 al 4.")