
import json
import os

from carbon_verifier import WebhookVerifier
from dotenv import load_dotenv

load_dotenv()
# Initialize the verifier with your signing key
SIGNING_SECRET = os.getenv("CARBON_WEBHOOK_SIGNATURE", "")
verifier = WebhookVerifier(SIGNING_SECRET)

def verify_webhook(headers, payload):
    carbon_signature = headers.get('Carbon-Signature')
    if not carbon_signature:
        return {'status': 'error', 'message': 'Missing Carbon-Signature header'}, 400

    try:
        timestamp, received_signature = WebhookVerifier.extract_signature_header(carbon_signature)
    except ValueError:
        return {'status': 'error', 'message': 'Invalid Carbon-Signature header format'}, 400

    if not verifier.validate_signature(received_signature, timestamp, payload):
        return {'status': 'error', 'message': 'Invalid signature'}, 400

    data = json.loads(payload)
    print("Received webhook data:", data)

    # Handle the event
    event_type = data.get('webhook_type')
    if event_type == 'example_event':
        # Process the event
        print("Processing example_event")

    return {'status': 'success'}, 200

# hardcoded payload for example
payload_v1 = '{"payload": "{\\"webhook_type\\": \\"FILES_CREATED\\", \\"obj\\": {\\"object_type\\": \\"FILE_LIST\\", \\"object_id\\": [\\"46654\\"], \\"additional_information\\": \\"null\\"}, \\"customer_id\\": \\"satvik\\", \\"timestamp\\": \\"1721392406\\"}"}'

# hardcoded header for example
headers = {
  "Content-Type": "application/json",
  "Carbon-Signature": "t=1721392406,v1=aa2273ab64bb9162e7e7983a9cd7ab9f90d686691b1fd25c577991ad42c53fc1",
  "Carbon-Signature-Compact": "t=1721392406,v2=42a86d4083fee090b5a0800a91e82fb389f0bed4da757d07ee8ba97485194e59"
}

result, status_code = verify_webhook(headers, payload_v1)
print(f"Verification Result: {result}, Status Code: {status_code}")
