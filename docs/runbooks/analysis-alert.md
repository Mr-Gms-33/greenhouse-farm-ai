# Financial analysis user-impact alert

## Signal

Alert `FinancialAnalysisJourneyFailing` or `FinancialAnalysisHighLatency` based on journey metrics, not CPU.

## Demo drill

```powershell
curl -X POST http://localhost:8089/demo/trigger -H "X-Webhook-Secret: dev-responder-secret"
```

Expected:

1. API force-failure flag enabled.
2. Responder clears failure and enables summary-only mode.
3. Journey health returns ok.
4. Incident recorded at `/incidents` and optionally via API.

## Manual remediation

Allowlisted only:

- Enable summary-only mode
- Clear demo force-failure flag
- Verify journey health

Forbidden: arbitrary shell, DB writes to sales/expenses, automatic code deploy.
