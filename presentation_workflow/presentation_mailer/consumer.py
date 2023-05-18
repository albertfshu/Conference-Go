import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()

# added 05-17
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()
channel.queue_declare(queue="presentation_approvals")
channel.queue_declare(queue="presentation_rejections")


def process_approval(ch, method, properties, body):
    message = json.loads(body)
    presenter_email = message["presenter_email"]
    presenter_name = message["presenter_name"]
    title = message["title"]
    subject = "Your presentation has been accepted"
    body = f"{presenter_name}, we're happy to tell you that your presentation {title} has been accepted"
    send_mail(
        subject=subject,
        message=body,
        from_email="admin@conference.go",
        recipient_list=[presenter_email],
    )


def process_rejection(ch, method, properties, body):
    message = json.loads(body)
    presenter_email = message["presenter_email"]
    presenter_name = message["presenter_name"]
    title = message["title"]
    subject = "Your presentation has been rejected"
    body = f"{presenter_name}, we regret to inform you that your presentation has been rejected"
    send_mail(
        subject=subject,
        message=body,
        from_email="admin@conference.go",
        recipient_list=[presenter_email],
    )


while True:
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="rabbitmq")
        )
        channel = connection.channel()
        channel.queue_declare(queue="presentation_approvals")
        channel.basic_consume(
            queue="presentation_approvals",
            on_message_callback=process_approval,
            auto_ack=True,
        )

        channel.queue_declare(queue="presentation_rejections")
        channel.basic_consume(
            queue="presentation_rejections",
            on_message_callback=process_rejection,
            auto_ack=True,
        )
        print("waiting for messages...")
        channel.start_consuming()
    except AMQPConnectionError:
        print("Could not connect to RabbitMQ")
        time.sleep(2.0)

# added 05-17
channel.basic_consume(
    queue="presentation_approvals",
    on_message_callback=approve,
    auto_ack=True,
)
channel.basic_consume(
    queue="presentation_rejections",
    on_message_callback=reject,
    auto_ack=True,
)
channel.start_consuming()

# def process_message(ch, method, properties, body):
#     parameters = pika.ConnectionParameters(host="rabbitmq")
#     connection = pika.BlockingConnection(parameters)
#     channel = connection.channel()
#     channel.queue_declare(queue="presentation_approvals")
#     channel.basic_consume(
#         queue="presentation_approvals",
#         on_message_callback=process_message,
#         auto_ack=True,
#     )
