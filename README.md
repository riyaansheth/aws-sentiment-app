# Sentiment Analysis Web App (AWS Serverless)

Cloud Application Development mini-project. Paste text, get sentiment (POSITIVE / NEGATIVE / NEUTRAL / MIXED) with confidence scores.

## Architecture
Browser → API Gateway (HTTP API) → Lambda (Python 3.12) → Comprehend `DetectSentiment`
                                        └→ S3 (stores every result as JSON)

## AWS services (4)
| Service | Role |
|---|---|
| Amazon API Gateway | Public HTTPS endpoint, routes GET / and POST /analyze |
| AWS Lambda | Serves the frontend on GET, runs analysis on POST |
| Amazon Comprehend | NLP sentiment detection |
| Amazon S3 | Persists results (`results/<uuid>.json`) |

Plus IAM (execution role) and CloudWatch Logs. Region: ap-southeast-2. All free tier.

## Files
- `lambda_function.py` – entire backend + embedded frontend
- `DEPLOY.md` – console deploy steps
- `screenshots/` – deployment evidence for the report
