INSTALL httpfs;
LOAD httpfs;
SET s3_url_style='path';
SET s3_endpoint='localhost:9000';
SET s3_use_ssl='false';



SELECT
    *
FROM read_json_auto('s3://raw/pokemons_raw/pokemons_list/20241001_151305.json');

SELECT
    *
FROM read_parquet('s3://bronze/pokemons_bronze/pokemons_list/20241001_151305.parquet');