# AlFilaha Pro frontend

Static SPA based on `alfilaha_pro_6.html`, served by nginx as the Compose `web`
service on port 3000.

- Greenhouse construction planner (حاسبة بناء البيوت) removed
- Bilingual Arabic (RTL) / English (LTR) via the **English / العربية** toggle
- Login is farm-manager only: `manager@farm.ma` / `Manager123!`

## Rebuild

```powershell
python scripts/patch_alfilaha_en_no_builder.py
docker compose up --build -d web
```

`patch_alfilaha_en_no_builder.py` reinstalls the prototype, strips the builder,
and injects EN/AR i18n.
