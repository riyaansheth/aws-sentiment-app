"""Build the screenshot report PDF. Run: python3 make_pdf.py"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

SHOTS = [
    ("01-s3-bucket-created.png",       "Amazon S3 bucket created",
     "Bucket sentiment-app-riyaan in ap-southeast-2. Public access blocked. Lambda writes one JSON object per analysis under results/."),
    ("02-lambda-function-overview.png","AWS Lambda function overview",
     "Function sentimentFn on Python 3.14. The diagram shows the API Gateway trigger with three routes attached."),
    ("02b-lambda-code-editor.png",     "Lambda source code",
     "lambda_function.py handles GET / (frontend), POST /analyze (scoring and storage) and GET /history (DynamoDB scan)."),
    ("03-iam-execution-role.png",      "IAM execution role",
     "The function runs as PowerUserRole, which grants the S3 and DynamoDB permissions the code needs."),
    ("04-api-gateway-routes.png",      "Amazon API Gateway routes",
     "HTTP API sentiment-api with routes GET /, POST /analyze and GET /history, all integrated with the Lambda function. Stage $default auto-deploys."),
    ("05-dynamodb-table.png",          "Amazon DynamoDB table",
     "Table SentimentResults with partition key id, on-demand capacity."),
    ("06-s3-results-objects.png",      "Results stored in S3",
     "Each analysis is saved as results/<uuid>.json containing the text, label, scores and timestamp."),
    ("07-dynamodb-items.png",          "Results stored in DynamoDB",
     "The same results as items in the table, read back by the History view."),
    ("08a-app-landing.png",            "Live application: landing page",
     "The landing page served from the API Gateway URL. The orb sits in the centre and clicking it opens the analyzer."),
    ("08-app-live-result.png",         "Live application: analysis result",
     "The web app served from the API Gateway URL. Text entered, label and scores returned by the Lambda function."),
    ("09-app-history.png",             "Live application: history",
     "The History view calls GET /history and lists previous readings from DynamoDB."),
]

W, H = landscape(A4)
out = "Screenshots_Report.pdf"
c = canvas.Canvas(out, pagesize=(W, H))
c.setTitle("Sentiment Analysis Web App on AWS: deployment screenshots")

# cover
c.setFont("Helvetica-Bold", 26); c.drawString(20*mm, H-40*mm, "Sentiment Analysis Web App on AWS")
c.setFont("Helvetica", 14); c.drawString(20*mm, H-50*mm, "Cloud Application Development mini-project: deployment screenshots")
c.setFont("Helvetica", 12)
y = H-70*mm
for line in [
    "Services used: Amazon API Gateway, AWS Lambda, Amazon DynamoDB, Amazon S3 (plus IAM and CloudWatch Logs)",
    "Region: Asia Pacific (Sydney), ap-southeast-2",
    "Live URL: https://9b0jyd6730.execute-api.ap-southeast-2.amazonaws.com/",
    "Source code: https://github.com/riyaansheth/aws-sentiment-app",
    "", "Contents:"] + [f"  {i+1}. {t}" for i,(_,t,_) in enumerate(SHOTS)]:
    c.drawString(20*mm, y, line); y -= 7*mm
c.showPage()

for i,(fn,title,caption) in enumerate(SHOTS, 1):
    path = os.path.join("screenshots", fn)
    if not os.path.exists(path): continue
    c.setFont("Helvetica-Bold", 18); c.drawString(15*mm, H-18*mm, f"{i}. {title}")
    c.setFont("Helvetica", 10.5); c.drawString(15*mm, H-25*mm, caption)
    img = ImageReader(path); iw, ih = img.getSize()
    maxw, maxh = W-30*mm, H-40*mm
    s = min(maxw/iw, maxh/ih); dw, dh = iw*s, ih*s
    c.drawImage(img, (W-dw)/2, 10*mm, dw, dh, preserveAspectRatio=True)
    c.setFont("Helvetica", 8); c.drawRightString(W-15*mm, 5*mm, f"{i} / {len(SHOTS)}")
    c.showPage()
c.save(); print("wrote", out)
