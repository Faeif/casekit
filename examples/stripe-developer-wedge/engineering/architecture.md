# Engineering Architecture: Stripe Developer Wedge

```
[ Customer Browser ] 
        │ (Stripe.js tokenization)
        ▼
[ Stripe Token Vault (PCI-DSS Level 1) ] ── (Single-use Token `tok_123`) ──► [ Merchant Server ]
                                                                                   │
                                                                                   ▼ (7 Lines API Call)
                                                                            [ Stripe API Core ]
                                                                                   │
                                                                                   ▼
                                                                     [ Acquiring Bank / Card Networks ]
```

## Core Architectural Guarantees
1. **PCI-DSS Scope Elimination**: Raw Primary Account Numbers (PANs) never touch the merchant web server.
2. **Idempotency**: All `POST /v1/charges` API requests support `Idempotency-Key` headers in PostgreSQL.
3. **Webhook Reliability**: Guaranteed at-least-once delivery for `charge.succeeded` and `charge.refunded` events.
