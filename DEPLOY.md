# Deploy (AWS console, ap-southeast-2, Free Plan)

## 1. S3
Create bucket `sentiment-app-riyaan`, all defaults (private).

## 2. DynamoDB
Create table `SentimentResults`, partition key `id` (String), default settings (on-demand).

## 3. Lambda
- Create function `sentimentFn`, Python 3.14, author from scratch.
- Code → Update → Upload .zip → `function.zip` (zip of lambda_function.py).
- Configuration → Environment variables: `BUCKET=sentiment-app-riyaan`, `TABLE=SentimentResults`.
- Configuration → General → Timeout 15 s.
- Permissions: execution role must allow s3:PutObject on the bucket and dynamodb:PutItem/Scan on the table. (Free Plan default role `PowerUserRole` already has this.)

## 4. API Gateway
- Create HTTP API `sentiment-api`, integration = Lambda `sentimentFn`.
- Routes: `GET /`, `POST /analyze`, `GET /history`, all → sentimentFn.
- Stage `$default`, auto-deploy.

## 5. Test
```
U=https://<api-id>.execute-api.ap-southeast-2.amazonaws.com
curl $U/                       # HTML page
curl -X POST $U/analyze -H "content-type: application/json" -d '{"text":"I love this"}'
curl $U/history
```
