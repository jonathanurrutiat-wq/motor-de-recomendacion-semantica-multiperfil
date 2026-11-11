import numpy as np

from src.embeddings_previos import (codificar_reutilizando, fuente_del_lote, lotes_de_coleccion,
                                    lotes_reemplazados, ultimos_por_fuente, vectores_previos)

VIEJO = "filtrado_reviews_2026-09-26_00-31-30"
NUEVO = "filtrado_reviews_2026-10-18_23-15-02"
OTRA = "filtrado_mis_resenias_2026-08-01_10-00-00"


class ColeccionFalsa:
    # Lo mínimo de una colección de Chroma que usa embeddings_previos.
    def __init__(self, filas):
        self.filas = filas  # (documento, embedding, lote)

    def count(self):
        return len(self.filas)

    def get(self, include, limit, offset):
        filas = self.filas[offset:offset + limit]
        return {"documents": [f[0] for f in filas], "embeddings": [f[1] for f in filas],
                "metadatas": [{"lote": f[2]} for f in filas]}


def test_fuente_del_lote():
    assert fuente_del_lote(NUEVO) == "reviews"
    assert fuente_del_lote(OTRA) == "mis_resenias"
    assert fuente_del_lote("otro_nombre") == "otro_nombre"


def test_ultimos_por_fuente(tmp_path):
    archivos = [tmp_path / f"{lote}.csv" for lote in (NUEVO, VIEJO, OTRA)]
    assert ultimos_por_fuente(archivos) == [tmp_path / f"{OTRA}.csv", tmp_path / f"{NUEVO}.csv"]


def test_lotes_reemplazados():
    assert lotes_reemplazados({VIEJO, NUEVO, OTRA}) == [VIEJO]
    assert lotes_reemplazados({NUEVO, OTRA}) == []


def test_vectores_previos_y_lotes():
    coleccion = ColeccionFalsa([("a", [1.0, 0.0], VIEJO), ("b", [0.0, 1.0], VIEJO), ("c", [1.0, 1.0], OTRA)])
    previos = vectores_previos(coleccion, {"a", "c", "z"})
    assert set(previos) == {"a", "c"}
    np.testing.assert_array_equal(previos["c"], [1.0, 1.0])
    assert lotes_de_coleccion(coleccion) == {VIEJO, OTRA}


def test_codificar_reutilizando():
    pedidos = []

    def codificar(textos):
        pedidos.append(list(textos))
        return np.array([[len(t), 0.0] for t in textos])

    previos = {"ya": np.array([9.0, 9.0], dtype="float32")}
    vectores, nuevos = codificar_reutilizando(["ya", "nuevo", "nuevo", "otro"], previos, codificar)
    assert pedidos == [["nuevo", "otro"]]   # sin repetir y sin los que ya estaban
    assert nuevos == 2
    np.testing.assert_array_equal(vectores, [[9, 9], [5, 0], [5, 0], [4, 0]])

    pedidos.clear()
    vectores, nuevos = codificar_reutilizando(["ya"], previos, codificar)
    assert pedidos == [] and nuevos == 0
