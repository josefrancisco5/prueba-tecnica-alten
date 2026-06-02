import requests
from google.cloud import bigquery
import pandas as pd
from typing import List, Dict


class APIDownloader:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def get_all_countries(self):
        try:
            url = f"{self.base_url}/all?fields=name,capital,region,population,area,currencies,languages"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error al descargar datos de la API: {e}")
            return []

class BigQueryUploader:
    def __init__(self, project_id: str, dataset_id: str, table_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.client = None
        self.table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    def connect(self) -> bool:
        try:
            self.client = bigquery.Client(project=self.project_id)
            print(f"Conectado a BigQuery: {self.project_id}")
            return True
        except Exception as e:
            print(f"Error al conectar con BigQuery: {e}")
            return False
    
    def create_table(self, schema: List[bigquery.SchemaField]) -> bool:
        try:
            table = bigquery.Table(self.table_ref, schema=schema)
            table = self.client.create_table(table, exists_ok=True)
            print(f"Tabla {self.table_id} creada o ya existe")
            return True
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
            return False
    
    def upload_data(self, data: List[Dict]) -> bool:
        try:
            df = pd.json_normalize(data)
            
            # Renombrar columnas con puntos para BigQuery
            df.columns = df.columns.str.replace('.', '_', regex=False)
            
            # Filtrar solo las columnas del esquema
            columns_to_keep = ['name_common', 'capital', 'region', 'population', 'area']
            df = df[[col for col in columns_to_keep if col in df.columns]]
            
            # Convertir arrays a strings
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list) else x)
            
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                schema=[
                    bigquery.SchemaField("name_common", "STRING"),
                    bigquery.SchemaField("capital", "STRING"),
                    bigquery.SchemaField("region", "STRING"),
                    bigquery.SchemaField("population", "INTEGER"),
                    bigquery.SchemaField("area", "FLOAT"),
                ]
            )
            
            job = self.client.load_table_from_dataframe(
                df, self.table_ref, job_config=job_config
            )
            job.result()
            
            print(f"Subidos {len(data)} registros a BigQuery en tabla {self.table_id}")
            return True
        except Exception as e:
            print(f"Error al subir datos a BigQuery: {e}")
            return False


def main():
    API_BASE_URL = "https://restcountries.com/v3.1"
    PROJECT_ID = "project-5b0d8e1f-190f-427b-88c"
    DATASET_ID = "SANDBOX_prueba_tecnica_alten"
    TABLE_ID = "countries"
    
    print("=" * 60)
    print("Iniciando proceso de descarga y subida de datos")
    print("=" * 60)
    
    print("\nDescargando datos de REST Countries API...")
    downloader = APIDownloader(API_BASE_URL)
    countries_data = downloader.get_all_countries()
    
    if not countries_data:
        print("No se pudieron descargar datos. Saliendo...")
        return
    
    if len(countries_data) > 100:
        countries_data = countries_data[:100]
    
    uploader = BigQueryUploader(PROJECT_ID, DATASET_ID, TABLE_ID)
    if not uploader.connect():
        print("No se pudo conectar a BigQuery. Saliendo...")
        return
    
    print("\nCreando tabla en BigQuery...")
    schema = [
        bigquery.SchemaField("name_common", "STRING"),
        bigquery.SchemaField("capital", "STRING"),
        bigquery.SchemaField("region", "STRING"),
        bigquery.SchemaField("population", "INTEGER"),
        bigquery.SchemaField("area", "FLOAT"),
    ]
    uploader.create_table(schema)
    
    print("\nSubiendo datos a BigQuery...")
    uploader.upload_data(countries_data)


if __name__ == "__main__":
    main()
