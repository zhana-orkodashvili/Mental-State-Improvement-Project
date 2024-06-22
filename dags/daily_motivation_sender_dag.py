from datetime import datetime
from logging import info

from pendulum import today
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException

from source.image_fetcher import get_random_image
from source.quote_fetcher import get_random_quote
from source.teams_notifier import create_payload, send_to_teams


def skip_on_holiday(**kwargs):
    holiday_dates = ['11.06', '13.06', '15.06', '25.06']
    today_date = datetime.now().strftime('%d.%m')
    if today_date in holiday_dates:
        info(f"Today ({today_date}) is a holiday. Skipping the task.")
        raise AirflowSkipException(f"Skipped execution on {today_date}")


with DAG(
        dag_id='daily_notification_dag',
        start_date=today(),
        schedule='@daily',
        tags=['notification', 'quote', 'image'],
        description='A DAG to send daily notifications with inspiring quotes and images',
        catchup=False
) as dag:
    check_holiday_task = PythonOperator(
        task_id='check_skip',
        python_callable=skip_on_holiday,
    )

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

    check_holiday_task >> [get_image_task, get_quote_task] >> create_payload_task >> send_notification_task
