from pathlib import Path
import hashlib
import re
import urllib.request

src = Path(r"d:\DSI_Laptop\Downl\alfilaha_pro_6.html").read_text(encoding="utf-8").replace("\r\n", "\n")
local = Path("apps/alfilaha/index.html").read_text(encoding="utf-8")
served = urllib.request.urlopen("http://localhost:3000/").read().decode("utf-8")

def strip_fonts(html: str) -> str:
    html = re.sub(
        r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\n',
        "",
        html,
    )
    html = re.sub(
        r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\n',
        "",
        html,
    )
    html = re.sub(
        r'<link href="https://fonts\.googleapis\.com/css2\?[^"]+" rel="stylesheet">\n',
        "",
        html,
    )
    return html

local_core = strip_fonts(local)
served_core = strip_fonts(served)

print("brand_local", "الفلاحة برو" in local)
print("brand_served", "الفلاحة برو" in served)
print("fonts_injected", "fonts.googleapis.com" in local)
print("local_core_eq_src", local_core == src)
print("served_eq_local", served == local)
print("src_len", len(src), "local_len", len(local), "served_len", len(served))
print("local_sha", hashlib.sha256(local.encode()).hexdigest()[:16])
print("served_sha", hashlib.sha256(served.encode()).hexdigest()[:16])

assert "الفلاحة برو" in local and "الفلاحة برو" in served
assert local_core == src, "local HTML diverges from prototype beyond font injection"
assert served == local, "served HTML diverges from apps/alfilaha/index.html"
print("PASS: 1:1 frontend verified")
