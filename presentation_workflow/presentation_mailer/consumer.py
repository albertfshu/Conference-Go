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

while True:
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters("rabbitmq")
        )
        channel = connection.channel()
        channel.queue_declare(queue="presentation_approvals")
        channel.queue_declare(queue="presentation_rejections")

        def reject(ch, method, properties, body):
            data = json.loads(body)
            email = data["presenter_email"]
            name = data["presenter_name"]
            title = data["title"]
            send_mail(
                "Your presentation has been rejected",
                f"We're sorry, {name}, but your presentation {title} has been rejected",
                "admin@conferece.go",
                [email],
                fail_silently=False,
            )

        def approve(ch, method, properties, body):
            data = json.loads(body)
            email = data["presenter_email"]
            name = data["presenter_name"]
            title = data["title"]
            send_mail(
                "Your presentation has been accepted",
                f"{name}, we're happy to tell you that your presentation {title} has been accepted",
                "admin@conferece.go",
                [email],
                fail_silently=False,
            )

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
    except AMQPConnectionError:
        print("Could not connect to RabbitMQ")
        time.sleep(2.0)
