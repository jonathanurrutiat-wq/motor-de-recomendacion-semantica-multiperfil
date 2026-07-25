import json
import os

archivo_perfiles = "perfiles.json"

if os.path.exists(archivo_perfiles):
    with open(archivo_perfiles, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
else:
    datos = {}

def mostrar_menu():
    print("\n" + "="*25)
    print("Menú de creación y visualización de perfiles")
    print("="*25)
    print("1. Crear/actualizar perfil")
    print("2. Mostrar perfiles existentes")
    print("3. Eliminar un perfil")
    print("4. Salir")
    print("="*25)

def modificar_perfil(datos):
    nombre_perfil = input("Ingrese el nombre de perfil (nuevo o existente): ")
    if nombre_perfil in datos:
        cambiar = input(f"El perfil '{nombre_perfil}' ya existe. ¿Desea cambiar su nombre? (s/n): ")
        if cambiar.lower() == "s":
            nuevo_nombre = input("Ingrese el nuevo nombre del perfil: ")
            if nuevo_nombre and nuevo_nombre != nombre_perfil:
                datos[nuevo_nombre] = datos.pop(nombre_perfil)
                print(f"El perfil ha sido renombrado a '{nuevo_nombre}'.")
                nombre_perfil = nuevo_nombre
    else:
        print(f"Creando un nuevo perfil: '{nombre_perfil}'")
        datos[nombre_perfil] = {"restrictivos": {}}
    
    if "restrictivos" not in datos[nombre_perfil]:
        datos[nombre_perfil]["restrictivos"] = {}
    
    while (True):
        filtro = input("Ingrese un restrictivo y su modificacion (escriba 'salir' para terminar): ")
        
        if filtro.lower() == "salir":
            break
        
        if filtro in datos[nombre_perfil]["restrictivos"]:
            modificar = input(f"El filtro '{filtro}' ya existe en el perfil '{nombre_perfil}', desea modificarlo? (s/n): ")
            if modificar == "s":
                datos[nombre_perfil]["restrictivos"].pop(filtro)
                
                filtro = input("Ingrese el nuevo filtro restrictivo: ")
            else :
                continue
        
        desc_texto = input("Ingrese la descripcion del filtro: ")
                        
        severidad = input("Ingrese la severidad del filtro (veto absoluto/intermedio/moderada): ")
        if (severidad.lower() == "veto absoluto"):
            nivel = "3"
        elif (severidad.lower() == "intermedio"):
            nivel = "2.5"
        elif (severidad.lower() == "moderada"):
            nivel = "2"
        else:
            print("Severidad no reconocida, se asignará 'moderada' por defecto.")
            nivel = "2"
                        
        excepcion = input("Ingrese la excepcion del filtro (si no hay, deje en blanco): ") or None
        datos[nombre_perfil]["restrictivos"][filtro] = {
            "descripcion_texto": desc_texto,
            "nivel": nivel,
            "severidad": severidad,
            "excepcion_texto": excepcion
        }
        print("Filtro agregado/modificado exitosamente.")
    
    if not datos[nombre_perfil]["restrictivos"]:
        print(f"El perfil '{nombre_perfil}' no tiene filtros restrictivos. Se eliminará el perfil.")
        del datos[nombre_perfil]

while True:
    mostrar_menu()
    opcion = input("Seleccione una opción: ")
    
    if opcion == "1":
        modificar_perfil(datos)
    
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
                    excepcion = detalles.get('excepcion_texto', 'Ninguna')
                    print(f"    Excepción: {excepcion}")
    
    elif opcion == "3":
        nombre_perfil = input("Ingrese el nombre del perfil a eliminar: ")
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
            