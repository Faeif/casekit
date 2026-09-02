# Threat Model: Stripe Developer Wedge

## Assets & Trust Boundaries
1. **Primary Account Numbers (PAN)**: Isolated in PCI Level 1 tokenization vault; encrypted with AES-256 GCM.
2. **API Secret Keys**: SHA-256 hashed and salted; rate-limited to 100 req/sec per merchant.
3. **Cardholder Data Flow**: Client browser directly communicates with `api.stripe.com` over TLS 1.3.
