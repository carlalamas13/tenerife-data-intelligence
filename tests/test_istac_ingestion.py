from src.ingestion.istac import build_url


def test_build_url() -> None:
    url = build_url(
        "C00065A_000036",
        "2.17",
        "csv",
        "https://datos.canarias.es/api/estadisticas/"
        "statistical-resources/v1.0/datasets/ISTAC",
    )

    assert url.endswith("/C00065A_000036/2.17.csv")