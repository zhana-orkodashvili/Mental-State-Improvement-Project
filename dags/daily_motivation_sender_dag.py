from pendulum import today
from airflow import DAG
from airflow.operators.python import PythonOperator

from source.image_fetcher import get_random_image
from source.quote_fetcher import get_random_quote
from source.teams_notifier import create_payload, send_to_teams

with DAG(
        dag_id='daily_notification_dag',
        start_date=today(),
        schedule=None,
        tags=['notification', 'quote', 'image'],
        description='A DAG to send daily notifications with inspiring quotes and images',
        catchup=False
) as dag:
    get_image_task = PythonOperator(
        task_id='get_random_image',
        python_callable=get_random_image,
    )

    get_quote_task = PythonOperator(
        task_id='get_random_quote',
        python_callable=get_random_quote,
    )

    create_payload_task = PythonOperator(
        task_id='create_payload',
        python_callable=create_payload,
    )

    send_notification_task = PythonOperator(
        task_id='send_to_teams',
        python_callable=send_to_teams,
    )

    [get_image_task, get_quote_task] >> create_payload_task >> send_notification_task
