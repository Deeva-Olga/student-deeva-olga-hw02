from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2

def publish_mart():
    conn = psycopg2.connect(host="localhost", database="dwh", user="airflow", password="airflow")
    cur = conn.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS published;")
    cur.execute("""
        DO $$
        BEGIN
            DROP TABLE IF EXISTS published.mart_daily_sales CASCADE;
            CREATE TABLE published.mart_daily_sales AS SELECT * FROM dwh_homework.mart_daily_sales;
        END $$;
    """)
    conn.commit()
    cur.close()
    conn.close()

with DAG(
    dag_id="elt_dwh_pipeline",
    start_date=datetime(2023, 10, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=['dwh', 'dbt']
) as dag:

    extract = BashOperator(
        task_id="extract_to_raw",
        bash_command="source /home/deeva/dwh_homework/venv/bin/activate && python /home/deeva/dwh_homework/scripts/extractor.py"
    )

    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command="source /home/deeva/dwh_homework/venv/bin/activate && cd /home/deeva/dwh_homework/dbt_project && dbt snapshot --profiles-dir ."
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="source /home/deeva/dwh_homework/venv/bin/activate && cd /home/deeva/dwh_homework/dbt_project && dbt run --profiles-dir ."
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="source /home/deeva/dwh_homework/venv/bin/activate && cd /home/deeva/dwh_homework/dbt_project && dbt test --profiles-dir ."
    )

    publish = PythonOperator(
        task_id="publish_mart",
        python_callable=publish_mart
    )

    extract >> dbt_snapshot >> dbt_run >> dbt_test >> publish
