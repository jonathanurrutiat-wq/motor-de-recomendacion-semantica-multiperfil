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
