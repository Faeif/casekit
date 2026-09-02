# API & Event Contracts: Stripe Developer Wedge

## 1. Charge Creation API (`POST /v1/charges`)

```bash
curl https://api.stripe.com/v1/charges \
  -u <STRIPE_SECRET_KEY>: \
  -d amount=2000 \
  -d currency=usd \
  -d card=tok_18924729104 \
  -d description="Charge for test@example.com"
```

### JSON Response Schema
```json
{
  "id": "ch_18924729104",
  "object": "charge",
  "amount": 2000,
  "currency": "usd",
  "paid": true,
  "refunded": false,
  "status": "succeeded"
}
```

## 2. Webhook Event Contracts
- `charge.succeeded`: Dispatched when credit card transaction clears acquiring gateway.
- `charge.failed`: Dispatched when transaction is declined with clear error code.
