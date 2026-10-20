import json, os, uuid, datetime, boto3

comprehend = boto3.client("comprehend")
s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET"]
CORS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"}

HTML = """<!doctype html><meta charset="utf-8"><title>Sentiment Analyzer</title>
<style>body{font-family:sans-serif;max-width:600px;margin:40px auto}textarea{width:100%;height:120px}
pre{background:#eee;padding:10px}.POSITIVE{color:green}.NEGATIVE{color:red}.NEUTRAL{color:gray}.MIXED{color:orange}</style>
<h2>Sentiment Analyzer</h2><p>S3 + Lambda + API Gateway + Comprehend</p>
<textarea id="t" placeholder="Type some text..."></textarea><br><br>
<button onclick="go()">Analyze</button>
<h3 id="s"></h3><pre id="out"></pre>
<script>
async function go(){
  out.textContent="...";
  const r=await fetch("analyze",{method:"POST",body:JSON.stringify({text:t.value})});
  const j=await r.json(); s.textContent=j.sentiment||j.error; s.className=j.sentiment||"";
  out.textContent=JSON.stringify(j,null,2);
}
</script>"""

def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    if method == "GET":
        return {"statusCode": 200, "headers": {"Content-Type": "text/html"}, "body": HTML}

    body = json.loads(event.get("body") or "{}")
    text = (body.get("text") or "").strip()
    if not text or len(text) > 5000:
        return {"statusCode": 400, "headers": CORS, "body": json.dumps({"error": "text must be 1-5000 chars"})}

    r = comprehend.detect_sentiment(Text=text, LanguageCode="en")
    result = {"id": str(uuid.uuid4()), "time": datetime.datetime.utcnow().isoformat(),
              "text": text, "sentiment": r["Sentiment"], "scores": r["SentimentScore"]}
    s3.put_object(Bucket=BUCKET, Key=f"results/{result['id']}.json", Body=json.dumps(result))
    return {"statusCode": 200, "headers": CORS, "body": json.dumps(result)}
