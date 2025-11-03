import os
from datetime import datetime, timezone, timedelta
import logging
import boto3
import pg8000
from aws_lambda_powertools.utilities import parameters


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        device_id = event["topic"].split("/")[-1]
        timestamp = datetime.fromisoformat(event["timestamp"])
        if timestamp.tzinfo is None:
            jst = timezone(timedelta(hours=9))
            timestamp = timestamp.replace(tzinfo=jst)
        status = event["status"]

        logger.info(f"Receive message: {event}")

    except Exception as e:
        logger.error(f"Fail to receive message: {event} - Error: {e}")
        return {"statusCode": 500, "error": str(e)}

    conn = None
    cursor = None

    try:
        conn = pg8000.connect(
            host=os.environ["DB_HOST"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=parameters.get_secret(os.environ["SSM_PASSWORD_NAME"]),
            port=5432,
        )

        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, device_name FROM "Iot_detail" WHERE device_id = %s""", (device_id,)
        )
        device_pk, device_name = cursor.fetchone()

        if device_pk is None:
            logger.warning(f"device_id '{device_id}' not found in DB")
        else:
            if status == "heartbeat":
                cursor.execute(
                    """
                    UPDATE "Iot_detail"
                    SET heartbeat_timestamp = %s
                    WHERE id = %s
                """,
                    (timestamp, device_pk),
                )

            elif status in ["open", "close"]:
                cursor.execute(
                    """
                    UPDATE "Iot_detail"
                    SET heartbeat_timestamp = %s
                    WHERE id = %s
                """,
                    (timestamp, device_pk),
                )
                cursor.execute(
                    """
                    INSERT INTO "Opencloselog" (device_id, openclose_timestamp, status)
                    VALUES (%s, %s, %s)
                """,
                    (device_pk, timestamp, status),
                )

            conn.commit()
            logger.info(f"Success to insert data: {event}")

    except Exception as e:
        logger.error(f"Fail to insert data: {event} - Error: {e}")
        return {"statusCode": 500, "error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    try:
        sns = boto3.client("sns")

        region = os.environ["AWS_REGION"]
        account_id = boto3.client("sts").get_caller_identity()["Account"]
        topic_arn = f"arn:aws:sns:{region}:{account_id}:{device_id}"

        if status in ["open", "close"]:
            if status == "open":
                message = "[通知] ドアが開きました！"
            else:
                message = "[通知] ドアが閉まりました！"

            sns.publish(TopicArn=topic_arn, Subject=f"ドアの状態通知：{device_name}", Message=message)

            logger.info(f"Success to send message: {message}")

    except sns.exceptions.NotFoundException:
        logger.warning(f"No SNS Topic: {topic_arn}")

    except Exception as e:
        logger.error(f"Fail to send message: {event} - Error: {e}")
        return {"statusCode": 500, "error": str(e)}

    logger.info(f"Event Successfully. Payload:{event}")
    return {"statusCode": 200, "body": f"Event Successfully. Payload:{event}"}