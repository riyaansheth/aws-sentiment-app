import json, os, re, uuid, datetime, decimal

if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    import boto3
    s3 = boto3.client("s3")
    table = boto3.resource("dynamodb").Table(os.environ["TABLE"])
    BUCKET = os.environ["BUCKET"]
CORS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"}

# ponytail: lexicon scorer (Comprehend is SCP-denied on AWS Free Plan); swap for comprehend.detect_sentiment on a paid account
POS = set("good great excellent amazing awesome love loved like liked happy fantastic wonderful best nice fun enjoy enjoyed perfect brilliant helpful easy smooth fast beautiful".split())
NEG = set("bad terrible awful horrible hate hated worst poor sad angry frustrating frustrated boring slow broken useless disappointing disappointed ugly difficult hard confusing annoying".split())
NEGATE = {"not", "no", "never", "n't", "dont", "don't", "cant", "can't", "isnt", "isn't", "wasnt", "wasn't"}

def score(text):
    words = re.findall(r"[a-z']+", text.lower())
    pos = sum(1 for i, w in enumerate(words) if w in POS and not (i and words[i-1] in NEGATE)) \
        + sum(1 for i, w in enumerate(words) if w in NEG and i and words[i-1] in NEGATE)
    neg = sum(1 for i, w in enumerate(words) if w in NEG and not (i and words[i-1] in NEGATE)) \
        + sum(1 for i, w in enumerate(words) if w in POS and i and words[i-1] in NEGATE)
    total = pos + neg
    if total == 0:
        return "NEUTRAL", {"Positive": 0.0, "Negative": 0.0, "Neutral": 1.0, "Mixed": 0.0}
    p, n = pos / total, neg / total
    if pos and neg and abs(p - n) < 0.34:
        label = "MIXED"
    else:
        label = "POSITIVE" if p > n else "NEGATIVE"
    return label, {"Positive": round(p, 3), "Negative": round(n, 3), "Neutral": 0.0, "Mixed": round(min(p, n) * 2, 3)}

HTML = """<!doctype html><meta charset="utf-8"><title>Sentiment Analyzer</title>
<style>body{font-family:sans-serif;max-width:600px;margin:40px auto}textarea{width:100%;height:120px}
pre{background:#eee;padding:10px}.POSITIVE{color:green}.NEGATIVE{color:red}.NEUTRAL{color:gray}.MIXED{color:orange}</style>
<h2>Sentiment Analyzer</h2><p>API Gateway + Lambda + DynamoDB + S3</p>
<textarea id="t" placeholder="Type some text..."></textarea><br><br>
<button onclick="go()">Analyze</button> <button onclick="hist()">History</button>
<h3 id="s"></h3><pre id="out"></pre>
<script>
async function go(){
  out.textContent="...";
  const r=await fetch("analyze",{method:"POST",body:JSON.stringify({text:t.value})});
  const j=await r.json(); s.textContent=j.sentiment||j.error; s.className=j.sentiment||"";
  out.textContent=JSON.stringify(j,null,2);
}
async function hist(){ s.textContent="History"; s.className=""; out.textContent=JSON.stringify(await (await fetch("history")).json(),null,2); }
</script>"""

def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    path = event.get("rawPath", "/")
    if method == "GET" and path == "/history":
        items = table.scan(Limit=20)["Items"]
        return {"statusCode": 200, "headers": CORS, "body": json.dumps(items, default=str)}
    if method == "GET":
        return {"statusCode": 200, "headers": {"Content-Type": "text/html"}, "body": HTML}

    body = json.loads(event.get("body") or "{}")
    text = (body.get("text") or "").strip()
    if not text or len(text) > 5000:
        return {"statusCode": 400, "headers": CORS, "body": json.dumps({"error": "text must be 1-5000 chars"})}

    try:
        label, scores = score(text)
        result = {"id": str(uuid.uuid4()), "time": datetime.datetime.utcnow().isoformat(),
                  "text": text, "sentiment": label, "scores": scores}
        s3.put_object(Bucket=BUCKET, Key=f"results/{result['id']}.json", Body=json.dumps(result))
        table.put_item(Item=json.loads(json.dumps(result), parse_float=decimal.Decimal))
        return {"statusCode": 200, "headers": CORS, "body": json.dumps(result)}
    except Exception as e:
        return {"statusCode": 500, "headers": CORS, "body": json.dumps({"error": str(e)})}

if __name__ == "__main__":
    assert score("I love this, it is great")[0] == "POSITIVE"
    assert score("this was terrible and boring")[0] == "NEGATIVE"
    assert score("not good at all")[0] == "NEGATIVE"
    assert score("the sky is blue")[0] == "NEUTRAL"
    print("ok")
