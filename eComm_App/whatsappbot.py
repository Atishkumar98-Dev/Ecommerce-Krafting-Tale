import http.client
import json

conn = http.client.HTTPSConnection("9lm6e4.api.infobip.com")
payload = json.dumps({
    "messages": [
        {
            "from": "447860099299",
            "to": "918652012693",
            "messageId": "1f1a32b0-9834-4ebe-b019-caae9cf60a4e",
            "content": {
                "templateName": "message_test",
                "templateData": {
                    "body": {
                        "placeholders": ["Atish"]
                    }
                },
                "language": "en"
            }
        }
    ]
})
headers = {
    'Authorization': 'App 92ddddd09315d89fb2f13abd3d17ce4e-91195aea-1908-497d-8bc4-be7854aa8136',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
conn.request("POST", "/whatsapp/1/message/template", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))