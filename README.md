# IoT Django App on AWS

A serverless Django backend for visualizing door sensor (open/close) status, powered by Raspberry Pi, Docker, and AWS Lambda.  

---

> ⚠️ This project is based on the open-source repository [fun-with-serverless/serverless-django](https://github.com/fun-with-serverless/serverless-django) by [@fun-with-serverless](https://github.com/fun-with-serverless), which I used as a learning resource and modified as part of my personal study and portfolio development.
> Licensed under the [MIT License](LICENSE).

---

## Overview

- Door status (open/close) collected via **Raspberry Pi GPIO**
- Sent via MQTT to AWS Lambda
- Stored in PostgreSQL and visualized through Django Admin UI
- Deployable using **AWS SAM**

---

## Use Case: "Home Monitoring System"

- Detect door open/close state with a magnetic sensor
- Send state changes to a Django backend via Lambda
- Monitor logs from anywhere
---

## Tech Stack

| Layer             | Technology                              |
|------------------|------------------------------------------|
| IoT Device       | Raspberry Pi (GPIO) + Python script      |
| Backend          | Django, Gunicorn                         |
| Containerization | Docker, Docker Compose                   |
| Database         | PostgreSQL                               |
| Deployment       | AWS Lambda (Container Image), SAM        |
| Infrastructure   | AWS CloudFormation, Secrets Manager      |
| DevOps           | AWS SAM CLI, GitHub                      |

---

## Architecture

```text
[Door Sensor] → [Raspberry Pi] → [MQTT] → [Lambda (Django)]
                                                      ↓
                                               [RDS: PostgreSQL]

```

## Quick Start (Local Dev)
```
git clone https://github.com/yourname/IoT-django-app-on-aws.git
docker-compose up -d
docker-compose exec app python manage.py migrate
```
Then open:
http://localhost:8000/admin

## Deploying to AWS
```
sam build
sam deploy --guided
```
> You'll need:  
> - A valid KeyPair name  
> - An S3 bucket (or use a managed one)  
> - AWS credentials configured (`aws configure`)  

## Environment Variables (excerpt)

| Variable               | Description                        |
|------------------------|------------------------------------|
| `DB_USER`              | PostgreSQL user                    |
| `DB_PASSWORD`          | DB password (in Secrets Manager)   |
| `DJANGO_SECRET_KEY`    | Django secret (in Secrets Manager) |
| `DJANGO_ALLOWED_HOSTS` | Lambda URL host                    |

---

## Folder Structure

```text
.
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
├── iot/                   # Django app
├── template.yaml            # AWS SAM template
└── README.md
```

## Original Work and License

This project is derived from:

> [fun-with-serverless/serverless-django](https://github.com/fun-with-serverless/serverless-django)  
> by [@fun-with-serverless](https://github.com/fun-with-serverless)

Licensed under the **MIT License**.  
See [`LICENSE`](LICENSE) for full text.

---

## Author

**Masayoshi Niki**  
IoT Engineer<br>
GitHub: [@Nikitty1226](https://github.com/Nikitty1226)

---

## License

Distributed under the MIT License.  
See [`LICENSE`](LICENSE) for details.