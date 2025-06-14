import os
from datetime import datetime
import boto3
import pg8000
from aws_lambda_powertools.utilities import parameters

def lambda_handler(event, context):
    try:
        status = event["status"]
        device_id = event["topic"].split("/")[-1]
        timestamp = datetime.fromisoformat(event["timestamp"])
        region = os.environ["AWS_REGION"]
        account_id = boto3.client("sts").get_caller_identity()["Account"]

        print(f"[INFO] Receive message:{event}")
    
    except Exception as e:
        return {"statusCode": 500, "error": str(e)}

    conn = None
    cursor = None

    try:
        conn = pg8000.connect(
            host=os.environ["DB_HOST"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=parameters.get_secret(os.environ["SSM_PASSWORD_NAME"]),
            port=5432
        )

        cursor = conn.cursor()
        
        print(f"[DEBUG] Running SELECT for device_id: {device_id}")
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"[DEBUG] Simple fetch result: {result}")

        cursor.execute("SELECT 1 FROM Iot_detail WHERE device_id = %s", (device_id,))
        result = cursor.fetchone()
        print(f"[DEBUG] fetchone() result: {result}")

        if status == "heartbeat":
            print(f"[DEBUG] Attempting heartbeat update for device_id: {device_id}")
            cursor.execute("""
                UPDATE Iot_detail
                SET heartbeat_timestamp = %s
                WHERE device_id = %s
            """, (timestamp, device_id))
            print(f"[DEBUG] Rows affected: {cursor.rowcount}")
            print("[DEBUG] Executed UPDATE for heartbeat")

        elif status in ["open", "close"]:
            cursor.execute("""
                INSERT INTO Opencloselog (device_id, openclose_timestamp, status)
                VALUES (%s, %s, %s)
            """, (device_id, timestamp, status))
            print("[DEBUG] Executed INSERT for open/close")

        conn.commit()

        print(f"[INFO] Success to insert data:{event}")
    
    except Exception as e:
        return {"statusCode": 500, "error": str(e)}

    finally:
        if cursor : cursor.close()
        if conn : conn.close()

    try:
        sns = boto3.client('sns')

        topic_arn = f"arn:aws:sns:{region}:{account_id}:{device_id}"

        if status in ["open", "close"]:
            if status == "open":
                message = "[通知] ドアが開きました！"
            else:
                message = "[通知] ドアが閉まりました！"

            sns.publish(
                TopicArn = topic_arn,
                Subject='ドアの状態通知',
                Message = message
            )

            print(f"[INFO] Success to send message:{message}")
        
    except sns.exceptions.NotFoundException:
        print(f"[WARN] No SNS Topic: {topic_arn}")

    except Exception as e:
        return {"statusCode": 500, "error": str(e)}

    print(f"[INFO] Event Successfully message:{event}")
    return {"statusCode": 200, "body": f"Event Successfully:{event}"}
