# Exercícios NoSQL

Repositório com as atividades práticas desenvolvidas na disciplina de Implementação e Gerenciamento de Bancos de Dados NoSQL.

## Grupo

- Vinicius José de Sousa
- Felipe Leal da Costa Martins Filho
- Luís Felipe Dias de Araújo Videres

## Exercícios

### 01 - OpenF1

Atividade utilizando dados da API OpenF1, com coleta e armazenamento dos dados em banco de dados NoSQL.

Inclui:

- Coleta de dados da OpenF1
- Armazenamento dos dados
- Consultas no MongoDB
- Evidências da execução
- Prática 04 - OpenF1
- Prática 05 - Análise dos dados e armazenamento de insights

### 02 - Cartola

Atividade de coleta e armazenamento de dados relacionados ao Cartola.

Inclui:

- Extração dos dados
- Processo de ETL
- Armazenamento no MongoDB
- Collections
- Documentos armazenados
- Evidências da execução

### 03 - Georreferenciamento

Atividade relacionada ao georreferenciamento de estabelecimentos de saúde.

Inclui:

- Dados de estabelecimentos do CNES
- Coleta e processamento dos dados
- Armazenamento de documentos GeoJSON
- MongoDB
- Índice geoespacial
- Evidências das consultas e execução

## Estrutura

```text
Exercicios-nosql_db/
│
├── exercicio01-openf1/
│   ├── evidencias/
│   ├── Pratica04-OpenF1/
│   ├── Pratica05/
│   ├── f1_data_coletor.py
│   └── requirements.txt
│
├── exercicio02-cartola/
│   ├── evidencias/
│   ├── cartola_etl.py
│   └── requirements.txt
│
└── exercicio03-georeferenciamento/
    ├── evidencias/
    ├── cnes_temp/
    ├── coletador_geojson.py
    ├── ubs.csv
    └── requirements.txt
