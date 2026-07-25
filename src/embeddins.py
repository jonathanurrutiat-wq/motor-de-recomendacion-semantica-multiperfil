import json
import chromadb

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

"""Proceso de chunkin del perfil"""

"""Chunkeador de prueba"""

sub_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function = len
)


def construir_chunk(perfiles:dict) -> list[Document]:
    documentos = []
    
    for perfil, categoria in perfiles.items():
        for tipo_categoria , filtros in categoria.items():
            
            for nombre_filtro, datos in filtros.items():
                partes = [f"Filtro: {nombre_filtro}"]
                partes.append(f"Descripcion: {datos.get("descripcion_texto", "  ")}")
                
                metadata = {
                    "persona": perfil,
                    "tipo": tipo_categoria,
                    "filtro": nombre_filtro,
                }
                
                
                if tipo_categoria == "restrictivos":
                    partes.append(f"Nivel : {datos.get("nivel")}")
                    partes.append(f"Severidad : {datos.get("severidad")}")
                    
                    if datos.get("corrupcion_directa"):
                        partes.append(f"Corrupcion Directa : {datos.get("corrupcion_directa")}")
                    
                    if datos.get("excepcion_texto"):
                         partes.append(f"Excepciones: {datos.get("excepcion_texto")}")
                         
                         
                    metadata["nivel"] = datos.get("nivel")
                    metadata["severidad"] = datos.get("severidad")
                    metadata["corrupcion_directa"] = datos.get("corrupcion_directa", [])
                    metadata["tiene_excepcion"] = bool(datos.get("excepcion_texto"))
                else:
                    partes.append(f"Importancia Base  {datos.get("importancia_base")}")
                    metadata["importancia_base"] = datos.get("importancia_base")

                        
                
                texto_chunk = "\n".join(partes)
                documentos.append(Document(page_content=texto_chunk, metadata=metadata))
                
    return documentos;
            
            
        
    




perfiles = {
    "Ignacio Araya": {
        "restrictivos": {
            "Camaradería Masculina Rancia": {
                "descripcion_texto": "Dinámicas que validan el sexismo desde el cinismo o la burla, donde la mujer es un trofeo o un chiste. Nota: No penaliza la 'protección masculina' o la nostalgia si la mirada de la película hacia el personaje femenino está construida desde la reverencia, el amor o la inocencia.",
                "descripcion_fragmentos": [
                    "Dinámicas que validan el sexismo desde el cinismo o la burla, donde la mujer es un trofeo o un chiste.",
                    "Nota: No penaliza la 'protección masculina' o la nostalgia si la mirada de la película hacia el personaje femenino está construida desde la reverencia, el amor o la inocencia.",
                ],
                "nivel": 3.0,
                "severidad": "Veto Absoluto",
                "corrupcion_directa": ["Resistencia Femenina"],
                "excepcion_texto": None,
                "excepcion_fragmentos": [],
            },
            "Insoportabilidad Prolongada": {
                "descripcion_texto": "Obligar al espectador a convivir excesivamente con personajes arrogantes, crueles o de una superioridad moral sofocante.",
                "descripcion_fragmentos": [
                    "Obligar al espectador a convivir excesivamente con personajes arrogantes, crueles o de una superioridad moral sofocante.",
                ],
                "nivel": 3.0,
                "severidad": "Veto Absoluto",
                "corrupcion_directa": ["Ternura y Empatía Radical", "Humanismo Social"],
                "excepcion_texto": "El personaje sufre un desarme temprano y su ego es bajado a tierra rápidamente. La película combina alta contemplación inmersiva y empatía radical para hacernos entender que la toxicidad nace de un trauma o abuso sistémico.",
                "excepcion_fragmentos": [
                    "El personaje sufre un desarme temprano y su ego es bajado a tierra rápidamente.",
                    "La película combina alta contemplación inmersiva y empatía radical para hacernos entender que la toxicidad nace de un trauma o abuso sistémico.",
                ],
            },
            "Control Emocional Artificial": {
                "descripcion_texto": "Perfección técnica fría, música manipuladora y montaje que clausura el temblor humano para dictar exactamente qué debes sentir.",
                "descripcion_fragmentos": [
                    "Perfección técnica fría, música manipuladora y montaje que clausura el temblor humano para dictar exactamente qué debes sentir.",
                ],
                "nivel": 2.5,
                "severidad": "Intermedio",
                "corrupcion_directa": ["Humanismo Social", "Contemplación Inmersiva"],
                "excepcion_texto": None,
                "excepcion_fragmentos": [],
            },
            "Personajes Diorama": {
                "descripcion_texto": "Estética de vitrina. Cuadros visualmente hermosos y simétricos, pero absolutamente vacíos de sangre y conexión humana real.",
                "descripcion_fragmentos": [
                    "Estética de vitrina.",
                    "Cuadros visualmente hermosos y simétricos, pero absolutamente vacíos de sangre y conexión humana real.",
                ],
                "nivel": 2.5,
                "severidad": "Intermedio",
                "corrupcion_directa": ["Ternura y Empatía Radical"],
                "excepcion_texto": None,
                "excepcion_fragmentos": [],
            },
            "Caos Asfixiante": {
                "descripcion_texto": "Caos hiperactivo, montaje frenético, dar las respuestas servidas sin dejar respirar a la narrativa.",
                "descripcion_fragmentos": [
                    "Caos hiperactivo, montaje frenético, dar las respuestas servidas sin dejar respirar a la narrativa.",
                ],
                "nivel": 2.0,
                "severidad": "Moderada",
                "corrupcion_directa": ["Contemplación Inmersiva"],
                "excepcion_texto": None,
                "excepcion_fragmentos": [],
            },
        },
        "afinidad": {
            "Resistencia Femenina": {
                "descripcion_texto": "Agencia y dignidad en la adversidad. Mujeres complejas, redes de apoyo, respuesta activa frente a injusticias, o la valentía de elegir el amor, la vulnerabilidad y el cuidado dentro de entornos hostiles o trágicos.",
                "descripcion_fragmentos": [
                    "Agencia y dignidad en la adversidad.",
                    "Mujeres complejas, redes de apoyo, respuesta activa frente a injusticias, o la valentía de elegir el amor, la vulnerabilidad y el cuidado dentro de entornos hostiles o trágicos.",
                ],
                "importancia_base": 10.0,
            },
            "Contemplación Inmersiva": {
                "descripcion_texto": "La 'calma aterradora'. Ritmo paciente que da oxígeno para procesar conflictos y tragedias. El tiempo y el espacio narrativo respiran.",
                "descripcion_fragmentos": [
                    "La 'calma aterradora'.",
                    "Ritmo paciente que da oxígeno para procesar conflictos y tragedias.",
                    "El tiempo y el espacio narrativo respiran.",
                ],
                "importancia_base": 9.0,
            },
            "Ternura y Empatía Radical": {
                "descripcion_texto": "La ética del cuidado. Empatía radical hacia lo roto, gestos mínimos, compasión genuina por las fallas humanas. Mirada libre de cinismo.",
                "descripcion_fragmentos": [
                    "La ética del cuidado.",
                    "Empatía radical hacia lo roto, gestos mínimos, compasión genuina por las fallas humanas.",
                    "Mirada libre de cinismo.",
                ],
                "importancia_base": 10.0,
            },
            "Humanismo Social": {
                "descripcion_texto": "Retrato crudo de la realidad. Naturalismo ético, comprensión del origen de la marginalidad, el trauma o la clase, observando sin superioridad moral ni juzgar a los afectados.",
                "descripcion_fragmentos": [
                    "Retrato crudo de la realidad.",
                    "Naturalismo ético, comprensión del origen de la marginalidad, el trauma o la clase, observando sin superioridad moral ni juzgar a los afectados.",
                ],
                "importancia_base": 8.0,
            },
            "Vanguardia y Simbolismo": {
                "descripcion_texto": "Riesgo y forma cinematográfica. Narrativas abiertas, pensamiento visual, significado que nace del desvío, la contradicción y el rechazo a fórmulas empaquetadas.",
                "descripcion_fragmentos": [
                    "Riesgo y forma cinematográfica.",
                    "Narrativas abiertas, pensamiento visual, significado que nace del desvío, la contradicción y el rechazo a fórmulas empaquetadas.",
                ],
                "importancia_base": 7.0,
            },
        },
    }
}


construir_chunk(perfiles)