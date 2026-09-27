import os
import pandas as pd
import geopandas as gpd
from pymongo import MongoClient
from shapely.geometry import Point

NOME_ARQUIVO = "ubs.csv"
MONGO_URI = "mongodb://localhost:27017/"
NOME_BANCO = "geodados"
NOME_COLECAO = "unidades_saude"

def verificar_arquivo():
    print("Verificando arquivo de dados...")

    if not os.path.exists(NOME_ARQUIVO):
        print(f"Arquivo '{NOME_ARQUIVO}' não encontrado.")
        return False

    tamanho = os.path.getsize(NOME_ARQUIVO)

    if tamanho == 0:
        print("O arquivo CSV está vazio.")
        return False

    print(f"Arquivo encontrado: {NOME_ARQUIVO}")
    print(f"Tamanho: {tamanho / 1024 / 1024:.2f} MB")

    return True

def processar_dados():
    print("\nProcessando dados...")

    try:
        df = pd.read_csv(
            NOME_ARQUIVO,
            sep=';',
            encoding='latin-1',
            low_memory=False
        )
    except Exception:
        df = pd.read_csv(
            NOME_ARQUIVO,
            encoding='utf-8',
            low_memory=False
        )

    print(f"Colunas encontradas: {len(df.columns)}")
    print(f"Registros encontrados: {len(df)}")

    df.columns = [
        str(col).strip().upper()
        for col in df.columns
    ]

    if 'NU_LATITUDE' in df.columns:
        coluna_latitude = 'NU_LATITUDE'
    elif 'LATITUDE' in df.columns:
        coluna_latitude = 'LATITUDE'
    else:
        raise ValueError("Não foi encontrada uma coluna de latitude.")

    if 'NU_LONGITUDE' in df.columns:
        coluna_longitude = 'NU_LONGITUDE'
    elif 'LONGITUDE' in df.columns:
        coluna_longitude = 'LONGITUDE'
    else:
        raise ValueError("Não foi encontrada uma coluna de longitude.")

    def encontrar_coluna(*nomes):
        for nome in nomes:
            if nome in df.columns:
                return nome
        return None

    coluna_uf = encontrar_coluna(
        'NO_UF',
        'UF',
        'SG_UF'
    )

    coluna_municipio = encontrar_coluna(
        'NO_MUNICIPIO_GESTOR',
        'MUNICIPIO',
        'NO_MUNICIPIO'
    )

    coluna_cnes = encontrar_coluna(
        'CO_CNES',
        'CNES'
    )

    coluna_logradouro = encontrar_coluna(
        'NO_LOGRADOURO',
        'LOGRADOURO'
    )

    coluna_bairro = encontrar_coluna(
        'NO_BAIRRO',
        'BAIRRO'
    )

    coluna_cep = encontrar_coluna(
        'CO_CEP',
        'CEP'
    )

    coluna_telefone = encontrar_coluna(
        'NU_TELEFONE',
        'TELEFONE'
    )

    coluna_cod_uf = encontrar_coluna(
        'CO_UF',
        'COD_UF'
    )

    coluna_cod_municipio = encontrar_coluna(
        'CO_MUNICIPIO_GESTOR',
        'COD_MUNICIPIO'
    )

    dados = pd.DataFrame()

    dados['cod_uf'] = df[coluna_cod_uf] if coluna_cod_uf else None
    dados['uf'] = df[coluna_uf] if coluna_uf else None
    dados['cod_municipio'] = df[coluna_cod_municipio] if coluna_cod_municipio else None
    dados['municipio'] = df[coluna_municipio] if coluna_municipio else None
    dados['cod_cnes'] = df[coluna_cnes] if coluna_cnes else None
    dados['latitude'] = df[coluna_latitude]
    dados['longitude'] = df[coluna_longitude]
    dados['logradouro'] = df[coluna_logradouro] if coluna_logradouro else None
    dados['bairro'] = df[coluna_bairro] if coluna_bairro else None
    dados['cep'] = df[coluna_cep] if coluna_cep else None
    dados['telefone'] = df[coluna_telefone] if coluna_telefone else None

    dados['latitude'] = (
        dados['latitude']
        .astype(str)
        .str.replace(',', '.', regex=False)
    )

    dados['longitude'] = (
        dados['longitude']
        .astype(str)
        .str.replace(',', '.', regex=False)
    )

    dados['latitude'] = pd.to_numeric(
        dados['latitude'],
        errors='coerce'
    )

    dados['longitude'] = pd.to_numeric(
        dados['longitude'],
        errors='coerce'
    )

    dados = dados.dropna(
        subset=['latitude', 'longitude']
    )

    dados = dados[
        (dados['latitude'] >= -90) &
        (dados['latitude'] <= 90) &
        (dados['longitude'] >= -180) &
        (dados['longitude'] <= 180)
    ]

    print(
        f"Dados processados: {len(dados)} registros com coordenadas válidas"
    )

    geometry = [
        Point(longitude, latitude)
        for longitude, latitude in zip(
            dados['longitude'],
            dados['latitude']
        )
    ]

    gdf = gpd.GeoDataFrame(
        dados,
        geometry=geometry,
        crs="EPSG:4674"
    )

    geojson_data = gdf.to_json()

    print("Conversão para GeoJSON realizada com sucesso.")

    return geojson_data, gdf

def salvar_no_mongodb(geojson_data, gdf):
    print("\nConectando ao MongoDB...")

    try:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000
        )

        client.admin.command('ping')

        db = client[NOME_BANCO]
        collection = db[NOME_COLECAO]

        collection.delete_many({})

        features = []

        for _, row in gdf.iterrows():

            def valor_texto(valor):
                if pd.isna(valor):
                    return ""
                return str(valor)

            def valor_inteiro(valor):
                try:
                    return int(float(valor))
                except Exception:
                    return None

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(row["longitude"]),
                        float(row["latitude"])
                    ]
                },
                "properties": {
                    "cod_uf": valor_inteiro(row["cod_uf"]),
                    "uf": valor_texto(row["uf"]),
                    "cod_municipio": valor_inteiro(row["cod_municipio"]),
                    "municipio": valor_texto(row["municipio"]),
                    "cod_cnes": valor_inteiro(row["cod_cnes"]),
                    "logradouro": valor_texto(row["logradouro"]),
                    "bairro": valor_texto(row["bairro"]),
                    "cep": valor_texto(row["cep"]),
                    "telefone": valor_texto(row["telefone"])
                }
            }

            features.append(feature)

        if features:
            result = collection.insert_many(features)
            print(
                f"Inseridos {len(result.inserted_ids)} documentos no MongoDB."
            )

        collection.create_index(
            [("geometry", "2dsphere")]
        )

        print("Índice geoespacial 2dsphere criado com sucesso.")
        print(f"Banco: {NOME_BANCO}")
        print(f"Coleção: {NOME_COLECAO}")

        client.close()

        return True

    except Exception as e:
        print(f"Erro ao salvar no MongoDB: {e}")
        return False

def main():

    print("=" * 60)
    print("EXERCÍCIO 03 - GEOREFERENCIAMENTO COM MONGODB")
    print("=" * 60)

    if not verificar_arquivo():
        return

    try:
        geojson_data, gdf = processar_dados()
    except Exception as e:
        print(f"\nErro ao processar os dados: {e}")
        return

    sucesso = salvar_no_mongodb(
        geojson_data,
        gdf
    )

    if sucesso:
        print("\n" + "=" * 60)
        print("PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"Dados disponíveis em: {NOME_BANCO}.{NOME_COLECAO}")
        print("GeoJSON gerado em memória.")
        print("Índice geoespacial: geometry (2dsphere)")
    else:
        print("\nOcorreu um erro durante o processo.")

if __name__ == "__main__":
    main()