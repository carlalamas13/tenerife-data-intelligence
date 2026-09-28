CREATE TABLE IF NOT EXISTS raw.istac_ingestion_batch (
    ingestion_batch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_code TEXT NOT NULL,
    source_version TEXT NOT NULL,
    snapshot_date DATE NOT NULL,
    source_url TEXT NOT NULL,
    source_sha256 CHAR(64) NOT NULL,
    source_file_size_bytes BIGINT,
    source_file_name TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (
        dataset_code,
        source_version,
        snapshot_date,
        source_sha256
    )
);

CREATE TABLE IF NOT EXISTS raw.istac_c00065a_000036 (
    raw_row_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ingestion_batch_id BIGINT NOT NULL
        REFERENCES raw.istac_ingestion_batch (ingestion_batch_id),

    measure_name_es TEXT,
    measure_code TEXT,

    territory_name_es TEXT,
    territory_code TEXT,

    period_label_es TEXT,
    period_code TEXT,

    accommodation_type_name_es TEXT,
    accommodation_type_code TEXT,

    nationality_name_es TEXT,
    nationality_code TEXT,

    value NUMERIC(20, 10),

    observation_note_es TEXT,

    observation_status_name_es TEXT,
    observation_status_code TEXT,

    confidentiality_name_es TEXT,
    confidentiality_code TEXT,

    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_istac_c00065a_000036_batch
    ON raw.istac_c00065a_000036 (ingestion_batch_id);