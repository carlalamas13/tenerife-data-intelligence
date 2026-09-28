\set csv_file '/data/raw/istac/C00065A_000036/2026-09-23/dataset.csv'

INSERT INTO raw.istac_ingestion_batch (
    dataset_code,
    source_version,
    snapshot_date,
    source_url,
    source_sha256,
    source_file_size_bytes,
    source_file_name
)
VALUES (
    'C00065A_000036',
    '2.17',
    DATE '2026-09-23',
    'https://datos.canarias.es/api/estadisticas/statistical-resources/v1.0/datasets/ISTAC/C00065A_000036/2.17.csv',
    'eed3902efce360741893bc41ea339d70c4941a4af9cc2494e22dce804932ed47',
    73326587,
    'dataset.csv'
)
ON CONFLICT (
    dataset_code,
    source_version,
    snapshot_date,
    source_sha256
)
DO UPDATE SET
    dataset_code = EXCLUDED.dataset_code
RETURNING ingestion_batch_id \gset batch_

CREATE TEMP TABLE istac_c00065a_000036_load (
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
    confidentiality_code TEXT
);

COPY istac_c00065a_000036_load (
    measure_name_es,
    measure_code,
    territory_name_es,
    territory_code,
    period_label_es,
    period_code,
    accommodation_type_name_es,
    accommodation_type_code,
    nationality_name_es,
    nationality_code,
    value,
    observation_note_es,
    observation_status_name_es,
    observation_status_code,
    confidentiality_name_es,
    confidentiality_code
)
FROM :'csv_file'
WITH (
    FORMAT CSV,
    HEADER TRUE
);

INSERT INTO raw.istac_c00065a_000036 (
    ingestion_batch_id,
    measure_name_es,
    measure_code,
    territory_name_es,
    territory_code,
    period_label_es,
    period_code,
    accommodation_type_name_es,
    accommodation_type_code,
    nationality_name_es,
    nationality_code,
    value,
    observation_note_es,
    observation_status_name_es,
    observation_status_code,
    confidentiality_name_es,
    confidentiality_code
)
SELECT
    :batch_ingestion_batch_id,
    measure_name_es,
    measure_code,
    territory_name_es,
    territory_code,
    period_label_es,
    period_code,
    accommodation_type_name_es,
    accommodation_type_code,
    nationality_name_es,
    nationality_code,
    value,
    observation_note_es,
    observation_status_name_es,
    observation_status_code,
    confidentiality_name_es,
    confidentiality_code
FROM istac_c00065a_000036_load;