import numpy as np
import pytest

from src import pooling


@pytest.fixture
def chunks():
    rng = np.random.default_rng(0)
    # film_id -> (rango de la reseña, embeddings de sus chunks)
    return {f"peli-{i}": (np.repeat(np.arange(10), 3), rng.normal(size=(30, 8)).astype(np.float32)) for i in range(6)}


def test_representar_media_y_percentil(chunks):
    ids = list(chunks)
    media = pooling.representar(chunks, ids, "media")
    assert media.shape == (6, 8)
    np.testing.assert_allclose(media[0], chunks["peli-0"][1].mean(axis=0), rtol=1e-6)
    p90 = pooling.representar(chunks, ids, "p90")
    np.testing.assert_allclose(p90[0], np.percentile(chunks["peli-0"][1], 90, axis=0), rtol=1e-6)


def test_representar_limita_resenias(chunks):
    limitado = pooling.representar(chunks, ["peli-0"], "media", max_resenias=2)
    np.testing.assert_allclose(limitado[0], chunks["peli-0"][1][:6].mean(axis=0), rtol=1e-6)


def test_estrategia_desconocida(chunks):
    with pytest.raises(ValueError):
        pooling.representar(chunks, ["peli-0"], "moda")


def test_rasgos_frases(chunks):
    frase = chunks["peli-3"][1][0]
    # Criterio con descripción + 2 frases: 3 textos -> 6 rasgos (fracción y percentil 90 de cada uno).
    textos = {"gt_cols_x": (["descripción", "a", "b"], np.vstack([np.ones(8), frase, -frase]).astype(np.float32))}
    rasgos = pooling.rasgos_frases(chunks, list(chunks), textos)
    assert rasgos["gt_cols_x"].shape == (6, 6)
    assert np.all((rasgos["gt_cols_x"][:, :3] >= 0) & (rasgos["gt_cols_x"][:, :3] <= 1))
    # Con los umbrales calculados aparte se obtiene lo mismo.
    umbrales = pooling.umbrales_frases(chunks, textos)
    np.testing.assert_allclose(pooling.rasgos_frases(chunks, list(chunks), textos, umbrales=umbrales)["gt_cols_x"],
                               rasgos["gt_cols_x"])
    solo = pooling.rasgos_frases(chunks, list(chunks), textos, solo_descripcion=True)
    assert solo["gt_cols_x"].shape == (6, 2)


class ColeccionFalsa:
    # Imita lo que devuelve la colección "perfiles" de Chroma para una persona.
    def __init__(self, filas):
        self.filas = filas

    def get(self, where=None, include=None):
        return {"metadatas": [meta for meta, _ in self.filas], "embeddings": [vector for _, vector in self.filas]}


def perfil_de_prueba():
    return {"restrictivos": {"Caos": {"descripcion": "x"}},
            "afinidad": {"Ternura": {"descripcion": "y", "frases_resenia": ["a", "b"]}}}


def filas_de_prueba(con_frases=True):
    rng = np.random.default_rng(1)
    filas = [({"persona": "P", "tipo": "restrictivos", "filtro": "Caos"}, rng.normal(size=8)),
             ({"persona": "P", "tipo": "afinidad", "filtro": "Ternura"}, rng.normal(size=8))]
    if con_frases:
        # Desordenadas a propósito: el índice de la frase define su posición.
        filas += [({"persona": "P", "tipo": "frase_resenia", "filtro": "Ternura", "categoria": "afinidad", "indice": i},
                   rng.normal(size=8)) for i in (1, 0)]
    return filas


def test_textos_de_criterios_incluye_criterios_sin_frases():
    filas = filas_de_prueba()
    textos = pooling.textos_de_criterios(ColeccionFalsa(filas), "P", perfil_de_prueba())
    assert set(textos) == {"gt_cols_caos", "gt_afinidad_ternura"}
    nombres, vectores = textos["gt_cols_caos"]
    assert nombres == ["descripción"] and vectores.shape == (1, 8)
    nombres, vectores = textos["gt_afinidad_ternura"]
    assert nombres == ["descripción", "a", "b"] and vectores.shape == (3, 8)
    frase_0 = next(vector for meta, vector in filas if meta.get("indice") == 0)
    np.testing.assert_allclose(vectores[1], frase_0, rtol=1e-6)


def test_textos_de_criterios_solo_con_frases():
    textos = pooling.textos_de_criterios(ColeccionFalsa(filas_de_prueba()), "P", perfil_de_prueba(),
                                         incluir_sin_frases=False)
    assert set(textos) == {"gt_afinidad_ternura"}


def test_textos_de_criterios_omite_embeddings_desactualizados(capsys):
    # El perfil dice que Ternura tiene 2 frases, pero la base no las tiene (falta ejecutar el módulo 3).
    textos = pooling.textos_de_criterios(ColeccionFalsa(filas_de_prueba(con_frases=False)), "P", perfil_de_prueba())
    assert set(textos) == {"gt_cols_caos"}
    assert "Ternura" in capsys.readouterr().out


def test_textos_de_criterios_sin_embeddings_del_perfil(capsys):
    assert pooling.textos_de_criterios(ColeccionFalsa([]), "P", perfil_de_prueba()) == {}
    assert capsys.readouterr().out.count("[!]") == 1


def test_rasgos_de_criterios_con_y_sin_frases(chunks):
    textos = pooling.textos_de_criterios(ColeccionFalsa(filas_de_prueba()), "P", perfil_de_prueba())
    rasgos = pooling.rasgos_frases(chunks, list(chunks), textos)
    assert rasgos["gt_cols_caos"].shape == (6, 2)         # un texto: fracción de chunks y percentil 90
    assert rasgos["gt_afinidad_ternura"].shape == (6, 6)  # tres textos
