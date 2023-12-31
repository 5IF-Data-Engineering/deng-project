import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.postgres_operator import PostgresOperator

HOST = 'pipeline-api'
PORT = '8000'

default_args = {
    'owner': 'minh.ngo',
    'start_date': airflow.utils.dates.days_ago(1),
    'email': 'minh@mail.com',
    'email_on_failure': False,
    'email_on_retry': False,
}

dag = DAG(
    'staging_weather_dag',
    default_args=default_args,
    description='Staging Weather DAG',
    schedule_interval=None,
)

create_table_task = PostgresOperator(
    task_id='create_table_task',
    postgres_conn_id='postgres_staging',
    sql=f"""
        CREATE TABLE IF NOT EXISTS staging_weather (
            year integer,
            month integer,
            day integer NOT NULL,
            day_of_week varchar(255),
            day_type varchar(255) NOT NULL,
            hour integer NOT NULL,
            temperature double precision,
            humidity double precision,
            precipitation double precision,
            rain double precision,
            snowfall double precision,
            windspeed double precision
        ) PARTITION BY LIST (year);

        CREATE TABLE IF NOT EXISTS staging_weather_2017 PARTITION OF
        staging_weather FOR VALUES IN (2017);

        CREATE TABLE IF NOT EXISTS staging_weather_2018 PARTITION OF
        staging_weather FOR VALUES IN (2018);

        CREATE TABLE IF NOT EXISTS staging_weather_2019 PARTITION OF
        staging_weather FOR VALUES IN (2019);

        CREATE TABLE IF NOT EXISTS staging_weather_2020 PARTITION OF
        staging_weather FOR VALUES IN (2020);

        CREATE TABLE IF NOT EXISTS staging_weather_2021 PARTITION OF
        staging_weather FOR VALUES IN (2021);

        CREATE TABLE IF NOT EXISTS staging_weather_2022 PARTITION OF
        staging_weather FOR VALUES IN (2022);

        CREATE INDEX IF NOT EXISTS staging_weather_year_idx 
        ON staging_weather (year);

        CREATE INDEX IF NOT EXISTS staging_weather_full_idx
        ON staging_weather (year, month, day_type, hour);

        CREATE INDEX IF NOT EXISTS staging_weather_full_2_idx
        ON staging_weather (year, month, day, hour);
    """,
    dag=dag,
    autocommit=True,
)

charge_data = BashOperator(
    task_id='charge_data_postgres',
    bash_command=f'/opt/scripts/staging_weather.sh {HOST} {PORT}',
    dag=dag,
    trigger_rule='none_failed',
)

create_table_task >> charge_data