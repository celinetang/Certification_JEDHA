"""
To use this DAG, you need to set some variables within the Airflow UI:


- `S3BucketName`: the name of the S3 bucket where the data will be stored.
- PostgresSQL variable names

Also set the connection for the Postgres database and the AWS account.
"""


import json
import logging
from datetime import datetime

import pandas as pd
import requests
import glob
import os
import os
import boto3
import pandas as pd
from airflow import DAG
from airflow.hooks.S3_hook import S3Hook
from airflow.sensors.python import PythonSensor
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from s3toPostgres import S3ToPostgresOperator
from airflow.utils.task_group import TaskGroup


default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 7, 24),
}


def _detect_file(**context):
    """Detects if a file named `Real_Time_Payments_*.csv` is inside `./data/data_logs` folder.

    If yes, it saves the full path to XCom and return True. False otherwise.
    """
    data_logs_list = glob.glob("./data/data_logs/Real_time_payments_*.csv")
    if not data_logs_list:
        return False
    data_logs_filename = max(data_logs_list, key=os.path.getctime)
    context["task_instance"].xcom_push(key="data_logs_filename", value=data_logs_filename)
    return True


def _fetch_data_upload_S3(**context):
    """Fetches csv data from local and save it to S3.
    """
    data_logs_filename = context["task_instance"].xcom_pull(key="data_logs_filename")
    filename = data_logs_filename.split("/")[-1]
    # Connect to our S3 bucket and load the file
    # filename is the path to our file and key is the full path inside the
    # bucket
    s3_hook = S3Hook(aws_conn_id="aws_default")
    s3_hook.load_file(filename=data_logs_filename, key=filename, bucket_name=Variable.get("S3BucketName"))
    # Let's push the filename to the context so that we can use it later
    context["task_instance"].xcom_push(key="real_time_filename", value=filename)
    logging.info(f"Saved real time data data to {filename}")

def _clean_file(**context):
    data_logs_filename = context["task_instance"].xcom_pull(key="data_logs_filename")
    os.remove(data_logs_filename)


with DAG(dag_id="etl_dag", default_args=default_args, schedule_interval="@hourly", catchup=False) as dag:
    start = DummyOperator(task_id="start")

    detect_file = PythonSensor(
        task_id="detect_file",
        python_callable=_detect_file,
    )

    fetch_data = PythonOperator(task_id="fetch_data", python_callable=_fetch_data_upload_S3)

    transfer_data_to_postgres = S3ToPostgresOperator(
            task_id="transfer_data_to_postgres",
            table="real_time_data_3",
            bucket="{{ var.value.S3BucketName }}",
            key="{{ task_instance.xcom_pull(key='real_time_filename') }}",
            postgres_conn_id="postgres://cazwrmravtstuq:075ae49e5d51649a69ee7e0fbadd1b9e1cb3e4113e92dbf89ba49e1a4adf4f85@ec2-54-234-13-16.compute-1.amazonaws.com:5432/d7ojfso4s2fmat",
            aws_conn_id="aws_default",
        )

    concat_tables = PostgresOperator(task_id = 'move_data_to_another_table', 
                                     postgres_conn_id = "postgres://cazwrmravtstuq:075ae49e5d51649a69ee7e0fbadd1b9e1cb3e4113e92dbf89ba49e1a4adf4f85@ec2-54-234-13-16.compute-1.amazonaws.com:5432/d7ojfso4s2fmat", 
                                     sql = "INSERT INTO public.fraudtest_new (trans_date_trans_time, cc_num, merchant, category, amt, first, last, gender, street, city, state, zip, lat, long, city_pop, job, dob, trans_num, unix_time, merch_lat, merch_long, is_fraud, prediction) SELECT trans_date_trans_time, cc_num, merchant, category, amt, first, last, gender, street, city, state, zip, lat, long, city_pop, job, dob, trans_num, unix_time, merch_lat, merch_long, is_fraud, prediction FROM real_time_data;")

    clean_file = PythonOperator(task_id="clean_file", python_callable=_clean_file, trigger_rule="one_success")

    end = DummyOperator(task_id="end")

    start >> detect_file >> fetch_data >> transfer_data_to_postgres >> concat_tables >> clean_file >> end


