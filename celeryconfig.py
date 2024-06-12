import os

broker_url = os.getenv('CELERY_BROKER_URL')
result_backend = os.getenv('CELERY_RESULT_BACKEND')
accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
