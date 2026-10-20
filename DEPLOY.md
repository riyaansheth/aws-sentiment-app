# Deploy (AWS console, ~30 min, free tier)

Region: us-east-1 (Comprehend not in ap-south-1 Mumbai)

## 1. S3
- Create bucket `sentiment-<yourname>` (unique). Keep defaults.
- Later: upload index.html, enable Static website hosting (Properties), uncheck Block public access, add policy:
  {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::sentiment-<yourname>/index.html"}]}

## 2. Lambda
- Create function → Author from scratch → `sentimentFn`, Python 3.12.
- Paste lambda_function.py, Deploy.
- Configuration → Environment variables → BUCKET = sentiment-<yourname>
- Configuration → Permissions → click role → Add permissions → attach:
  - ComprehendReadOnly
  - AmazonS3FullAccess (or scope to your bucket)
- Timeout: 10 s.

## 3. API Gateway
- Create API → HTTP API → Add integration: Lambda → sentimentFn.
- Route: POST /analyze. Stage: $default, auto-deploy.
- CORS: Access-Control-Allow-Origin *, Allow-Headers *, Allow-Methods POST,OPTIONS.
- Copy Invoke URL → paste `<invoke-url>/analyze` into index.html API const.

## 4. Test
curl -X POST <invoke-url>/analyze -H "content-type: application/json" -d '{"text":"I love this course"}'
→ {"sentiment":"POSITIVE","scores":{...}}

Check S3 → results/ has a JSON per request. Screenshot everything for the report.

## Services used (4): S3, Lambda, API Gateway, Comprehend (+ IAM, CloudWatch logs)
