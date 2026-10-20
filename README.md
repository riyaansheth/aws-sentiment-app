# Sentiment Analysis Web App (AWS Serverless)

Cloud Application Development mini-project. Paste text, get sentiment (POSITIVE / NEGATIVE / NEUTRAL / MIXED) with scores. Every result is stored in S3 and DynamoDB, and a History view reads them back.

**Live:** https://9b0jyd6730.execute-api.ap-southeast-2.amazonaws.com/

## Architecture
```
Browser ──GET /────────▶ API Gateway (HTTP API) ──▶ Lambda ──▶ returns HTML page
Browser ──POST /analyze▶ API Gateway ──────────────▶ Lambda ──▶ score text
                                                       ├──▶ S3  results/<uuid>.json
                                                       └──▶ DynamoDB SentimentResults
Browser ──GET /history─▶ API Gateway ──────────────▶ Lambda ──▶ DynamoDB scan
```

## AWS services (4)
| Service | Role |
|---|---|
| Amazon API Gateway | Public HTTPS endpoint, routes GET /, POST /analyze, GET /history |
| AWS Lambda (Python 3.14) | Serves the frontend, scores sentiment, writes results |
| Amazon DynamoDB | Stores each result as an item (partition key `id`) |
| Amazon S3 | Stores each result as a JSON object under `results/` |

Also IAM (execution role) and CloudWatch Logs. Region: ap-southeast-2. All AWS Free Plan.

## Why no Comprehend
The account is on the AWS Free Plan, whose organisation Service Control Policy explicitly denies `comprehend:DetectSentiment` (error captured during testing). The scorer is a lexicon with negation handling inside Lambda; swapping it for `comprehend.detect_sentiment` is a one-line change on a paid account.

## Files
- `lambda_function.py` – entire backend + embedded frontend. Run `python3 lambda_function.py` for the self-check.
- `DEPLOY.md` – console deploy steps
- `screenshots/` – deployment evidence for the report
