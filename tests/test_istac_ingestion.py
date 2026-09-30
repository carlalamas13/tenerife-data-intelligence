from src.ingestion.istac import build_url, get_latest_version


def test_build_url() -> None:
    url = build_url(
        "C00065A_000036",
        "2.17",
        "csv",
        "https://datos.canarias.es/api/estadisticas/"
        "statistical-resources/v1.0/datasets/ISTAC",
    )

    assert url.endswith("/C00065A_000036/2.17.csv")

def test_get_latest_version(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "dataset": [
                    {
                        "selfLink": {
                            "href": (
                                "https://example.com/"
                                "C00065A_000036/1.9"
                            )
                        }
                    },
                    {
                        "selfLink": {
                            "href": (
                                "https://example.com/"
                                "C00065A_000036/2.17"
                            )
                        }
                    },
                    {
                        "selfLink": {
                            "href": (
                                "https://example.com/"
                                "C00065A_000036/2.18"
                            )
                        }
                    },
                    {
                        "selfLink": {
                            "href": (
                                "https://example.com/"
                                "C00065A_000036/10.0"
                            )
                        }
                    },
                ]
            }

    monkeypatch.setattr(
        "src.ingestion.istac.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    assert (
        get_latest_version(
            dataset_id="C00065A_000036",
            base_url="https://example.com",
        )
        == "10.0"
    )

def test_get_latest_loaded_version(monkeypatch):
    class FakeResult:
        stdout = "2.18\n"

    def fake_run(*args, **kwargs):
        return FakeResult()

    monkeypatch.setattr(
        "scripts.istac.run_pipeline.subprocess.run",
        fake_run,
    )

    from scripts.istac.run_pipeline import get_latest_loaded_version

    assert (
        get_latest_loaded_version("C00065A_000036")
        == "2.18"
    )