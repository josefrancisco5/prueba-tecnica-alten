from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(1900, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

with DAG(
    'test',
    default_args=default_args,
    schedule_interval='0 3 * * *', 
    catchup=False,
) as dag:
    start = DummyOperator(task_id='start')
    end = DummyOperator(task_id='end')
    
    start >> end
