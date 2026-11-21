from pathlib import Path
import shutil

src = Path(r"d:\DSI_Laptop\Downl\alfilaha_pro_6.html")
dst = Path("apps/alfilaha/index.html")
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dst)

text = dst.read_text(encoding="utf-8").replace("\r\n", "\n")
assert "الفلاحة برو" in text, "Arabic brand text missing after copy"

font = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@500;700;800;900'
    '&family=Tajawal:wght@400;500;700;800;900&display=swap" rel="stylesheet">\n'
)
if "fonts.googleapis.com" not in text:
    if "<head>\n" in text:
        text = text.replace("<head>\n", "<head>\n" + font, 1)
    else:
        text = text.replace("<head>", "<head>\n" + font, 1)

dst.write_text(text, encoding="utf-8", newline="\n")
assert "الفلاحة برو" in dst.read_text(encoding="utf-8")
print(f"installed {dst} ({dst.stat().st_size} bytes)")
