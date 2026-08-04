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

def menu_modificacion_perfil():
    print("\n" + "="*35)
    print("Menú de modificación de perfil")
    print("="*35)
    print("1. Modificar nombre de perfil")
    print("2. Agregar/Modificar filtro restrictivo")
    print("3. Eliminar filtro restrictivo")
    print("4. Volver al menú principal")
    print("="*35)

def main():
  while True:
      mostrar_menu()
      opcion = input("Seleccione una opción: ")
      
      if opcion == "1":
          nombre_perfil = input("\nIngrese un nombre de perfil: ")
          if nombre_perfil in datos:
              eleccion = input(f"El perfil '{nombre_perfil}' ya existe. ¿Desea modificarlo? (s/n): ")
              if eleccion.lower() != "s":
                  print("No se realizaron cambios en el perfil.")
                  continue
          else:
              print(f"Creando un nuevo perfil: '{nombre_perfil}'")
              datos[nombre_perfil] = {"restrictivos": {}}
          
          if "restrictivos" not in datos[nombre_perfil]:
              datos[nombre_perfil]["restrictivos"] = {}
          
          while(True):
              menu_modificacion_perfil()
              opcion_modificacion = input("Seleccione una opción: ")
              
              if opcion_modificacion == "1":
                  nuevo_nombre = input("Ingrese el nuevo nombre del perfil: ")
                  if nuevo_nombre and nuevo_nombre != nombre_perfil:
                      datos[nuevo_nombre] = datos.pop(nombre_perfil)
                      print(f"El perfil ha sido renombrado a '{nuevo_nombre}'.")
                      nombre_perfil = nuevo_nombre
                  else:
                      print("Nombre no válido o igual al anterior. No se realizaron cambios.")
              
              elif opcion_modificacion == "2":
                  filtro = input("Ingrese el filtro restrictivo a agregar/modificar: ")
                  if filtro in datos[nombre_perfil]["restrictivos"]:
                      modificar = input(f"El filtro '{filtro}' ya existe. ¿Desea modificarlo? (s/n): ")
                      if modificar.lower() == "s":
                          nuevo_filtro = input("Ingrese el nuevo filtro restrictivo (o deje en blanco si lo quiere mantener): ")
                          if nuevo_filtro and nuevo_filtro != filtro:
                              datos[nombre_perfil]["restrictivos"][nuevo_filtro] = datos[nombre_perfil]["restrictivos"].pop(filtro)
                              filtro = nuevo_filtro
                          else:
                              print("No se realizaron cambios en el filtro.")
                              continue
                  else:
                      print(f"Agregando un nuevo filtro restrictivo: '{filtro}'")
                      datos[nombre_perfil]["restrictivos"][filtro] = {}
                  
                  desc_texto = input("Ingrese la descripción del filtro: ")
                  severidad = input("Ingrese la severidad del filtro (veto absoluto/intermedio/moderada): ")
                  if severidad.lower() == "veto absoluto":
                      nivel = "3"
                  elif severidad.lower() == "intermedio":
                      nivel = "2.5"
                  elif severidad.lower() == "moderada":
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
              
              elif opcion_modificacion == "3":
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
              
              elif opcion_modificacion == "4":
                  print("Volviendo al menú principal.")
                  break

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

if __name__ == '__main__':
  main()