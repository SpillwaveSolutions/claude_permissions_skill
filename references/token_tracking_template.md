# Token Budget Tracking Template

Use this template to track token consumption during permission operations.

## Template

```
Token Budget Status:
- Tier 1 (Metadata): 100 tokens
- Tier 2 (SKILL.md): 2,250 tokens
- Workflow Guide: +{COST} tokens
- Reference Data: +{COST} tokens (surgical)
- Total: {TOTAL} tokens
- Status: {OK/WARNING} ({threshold})
```

## Example

```
Token Budget Status:
- Tier 1 (Metadata): 100 tokens
- Tier 2 (SKILL.md): 2,250 tokens
- Workflow Guide: +1,500 tokens
- Reference Data: +200 tokens (surgical)
- Total: 4,050 tokens
- Status: OK (Within budget <10,000)
```

## Thresholds

| Request Type | Budget | Warning |
|-------------|--------|---------|
| Simple (CLI tool) | <5,000 | >5,000 |
| Medium (project setup) | <7,000 | >7,000 |
| Complex (unknown tool) | <10,000 | >10,000 |
