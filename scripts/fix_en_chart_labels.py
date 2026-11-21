# -*- coding: utf-8 -*-
"""Make Chart.js labels and domain names bilingual in AlFilaha SPA."""
from __future__ import annotations

import json
import re
from pathlib import Path

HTML = Path("apps/alfilaha/index.html")

EXTRA = {
    "انقر عموداً لفتح القطعة": "Click a column to open the plot",
    "انقر عموداً لفتح": "Click a column to open",
    "عدد القطع": "Plot count",
    "لا توجد إيرادات مسجّلة بعد.": "No revenue recorded yet.",
    "ERP فلاحي": "Farm ERP",
    "بيت بلاستيكي 1": "Greenhouse 1",
    "بيت بلاستيكي 2": "Greenhouse 2",
    "بيت بلاستيكي 3": "Greenhouse 3",
    "أرض مفتوحة — الفراولة": "Open field — strawberry",
    "أرض مفتوحة - الفراولة": "Open field - strawberry",
    "خريف 2025": "Autumn 2025",
    "ربيع 2026": "Spring 2026",
    "طماطم": "Tomato",
    "فلفل": "Pepper",
    "فراولة": "Strawberry",
    "خيار": "Cucumber",
    "كوسة": "Zucchini",
    "بطيخ أصفر": "Yellow melon",
    "دلاح": "Watermelon",
    "بطاطس": "Potato",
    "بصل": "Onion",
    "لوبيا": "Beans",
    "فلفل حار": "Hot pepper",
    "باذنجان": "Eggplant",
    "البناء": "Construction",
    "الغرس": "Planting",
    "النمو": "Growth",
    "الحصاد": "Harvest",
    "التفكيك": "Dismantling",
    "مبيدات ومواد وقاية": "Pesticides & protection",
    "أسمدة": "Fertilizers",
    "سقي وماء": "Water & irrigation",
    "يد عاملة": "Labor",
    "بذور وشتلات": "Seeds & seedlings",
    "طاقة وكهرباء": "Energy & electricity",
    "مصاريف أخرى": "Other expenses",
    "قطعة": "plot",
}


def main() -> None:
    text = HTML.read_text(encoding="utf-8")

    # Merge EXTRA into I18N_EN
    m = re.search(r"var I18N_EN = (\{.*?\});\n", text, flags=re.S)
    if not m:
        raise SystemExit("I18N_EN not found")
    i18n = json.loads(m.group(1))
    i18n.update(EXTRA)
    # rebuild keys array is computed at runtime from Object.keys
    new_json = json.dumps(i18n, ensure_ascii=False, separators=(",", ":"))
    text = text[: m.start(1)] + new_json + text[m.end(1) :]

    # CROPS with en
    crops_new = """var CROPS = [
  {id:'tomate',  ar:'طماطم',  en:'Tomato', em:'🍅'},
  {id:'poivron', ar:'فلفل',   en:'Pepper', em:'🫑'},
  {id:'fraise',  ar:'فراولة', en:'Strawberry', em:'🍓'},
  {id:'concombre',ar:'خيار',  en:'Cucumber', em:'🥒'},
  {id:'courgette',ar:'كوسة',  en:'Zucchini', em:'🥒'},
  {id:'melon',   ar:'بطيخ أصفر',en:'Yellow melon',em:'🍈'},
  {id:'pasteque',ar:'دلاح',   en:'Watermelon', em:'🍉'},
  {id:'pdt',     ar:'بطاطس',  en:'Potato', em:'🥔'},
  {id:'oignon',  ar:'بصل',    en:'Onion', em:'🧅'},
  {id:'haricot', ar:'لوبيا',  en:'Beans', em:'🫛'},
  {id:'piment',  ar:'فلفل حار',en:'Hot pepper',em:'🌶️'},
  {id:'aubergine',ar:'باذنجان',en:'Eggplant',em:'🍆'}
];
function cropById(id){
  for(var i=0;i<CROPS.length;i++) if(CROPS[i].id===id) return CROPS[i];
  return {id:id,ar:id,en:id,em:'🌱'};
}
function cropLabel(c){
  var crop = (typeof c === 'string') ? cropById(c) : c;
  return crop.em + ' ' + ((LANG==='en' && crop.en) ? crop.en : crop.ar);
}
"""
    text = re.sub(
        r"var CROPS = \[[\s\S]*?function cropById\(id\)\{[\s\S]*?return \{id:id,ar:id,em:'🌱'\};\n\}",
        crops_new.rstrip(),
        text,
        count=1,
    )

    # COST_TYPES with en
    costs_new = """var COST_TYPES = [
  {id:'pesticide', ar:'مبيدات ومواد وقاية', en:'Pesticides & protection', icon:'🧪'},
  {id:'fertilizer',ar:'أسمدة',              en:'Fertilizers', icon:'🧴'},
  {id:'irrigation',ar:'سقي وماء',           en:'Water & irrigation', icon:'💧'},
  {id:'labor',     ar:'يد عاملة',           en:'Labor', icon:'👷'},
  {id:'seed',      ar:'بذور وشتلات',        en:'Seeds & seedlings', icon:'🌱'},
  {id:'energy',    ar:'طاقة وكهرباء',       en:'Energy & electricity', icon:'⚡'},
  {id:'other',     ar:'مصاريف أخرى',         en:'Other expenses', icon:'📦'}
];
function costTypeById(id){
  for(var i=0;i<COST_TYPES.length;i++) if(COST_TYPES[i].id===id) return COST_TYPES[i];
  return {id:id,ar:id,en:id,icon:'📦'};
}
function costTypeLabel(ct){
  var c = (typeof ct === 'string') ? costTypeById(ct) : ct;
  return (LANG==='en' && c.en) ? c.en : c.ar;
}
"""
    text = re.sub(
        r"var COST_TYPES = \[[\s\S]*?function costTypeById\(id\)\{[\s\S]*?return \{id:id,ar:id,icon:'📦'\};\n\}",
        costs_new.rstrip(),
        text,
        count=1,
    )

    # PHASES with en
    phases_new = """var PHASES = [
  {key:'build',  ar:'البناء',   en:'Construction', color:'#5B7B8A', icon:'🏗️'},
  {key:'plant',  ar:'الغرس',    en:'Planting', color:'#A0703C', icon:'🌱'},
  {key:'grow',   ar:'النمو',    en:'Growth', color:'#3FA15A', icon:'🌿'},
  {key:'harvest',ar:'الحصاد',   en:'Harvest', color:'#E8A317', icon:'🧺'},
  {key:'teardown',ar:'التفكيك', en:'Dismantling', color:'#9B8AA6', icon:'♻️'}
];
function phaseByKey(k){
  for(var i=0;i<PHASES.length;i++) if(PHASES[i].key===k) return PHASES[i];
  return PHASES[0];
}
function phaseLabel(ph){
  var p = (typeof ph === 'string') ? phaseByKey(ph) : ph;
  return (LANG==='en' && p.en) ? p.en : p.ar;
}
"""
    text = re.sub(
        r"var PHASES = \[[\s\S]*?function phaseByKey\(k\)\{[\s\S]*?return PHASES\[0\];\n\}",
        phases_new.rstrip(),
        text,
        count=1,
    )

    # Chart bars: translate plot names + dataset labels
    text = text.replace(
        "var labels = plots.map(function(p){ return p.name; });\n"
        "  dashCharts.bars = new Chart(cv,{\n"
        "    type:'bar',\n"
        "    data:{labels:labels, datasets:[\n"
        "      {label:'التكلفة', data:plots.map(function(p){ return plotTotalCost(p); }),\n"
        "       backgroundColor:'#A0703C', borderRadius:6, maxBarThickness:34},\n"
        "      {label:'الإيراد', data:plots.map(function(p){ return plotRevenue(p); }),\n"
        "       backgroundColor:'#3FA15A', borderRadius:6, maxBarThickness:34}\n"
        "    ]},",
        "var labels = plots.map(function(p){ return t(p.name); });\n"
        "  dashCharts.bars = new Chart(cv,{\n"
        "    type:'bar',\n"
        "    data:{labels:labels, datasets:[\n"
        "      {label:t('التكلفة'), data:plots.map(function(p){ return plotTotalCost(p); }),\n"
        "       backgroundColor:'#A0703C', borderRadius:6, maxBarThickness:34},\n"
        "      {label:t('الإيراد'), data:plots.map(function(p){ return plotRevenue(p); }),\n"
        "       backgroundColor:'#3FA15A', borderRadius:6, maxBarThickness:34}\n"
        "    ]},",
    )

    # Pie crop labels
    text = text.replace(
        "labels:crops.map(function(c){ return cropById(c).em+' '+cropById(c).ar; }),",
        "labels:crops.map(function(c){ return cropLabel(c); }),",
    )

    # Phase chart labels
    text = text.replace(
        "labels:PHASES.map(function(ph){ return ph.ar; }),\n"
        "      datasets:[{label:'عدد القطع', data:PHASES.map(function(ph){ return phaseCounts[ph.key]||0; }),\n"
        "        backgroundColor:PHASES.map(function(ph){ return ph.color; }), borderRadius:6, maxBarThickness:30}]",
        "labels:PHASES.map(function(ph){ return phaseLabel(ph); }),\n"
        "      datasets:[{label:t('عدد القطع'), data:PHASES.map(function(ph){ return phaseCounts[ph.key]||0; }),\n"
        "        backgroundColor:PHASES.map(function(ph){ return ph.color; }), borderRadius:6, maxBarThickness:30}]",
    )

    # Phase tooltip "قطعة"
    text = text.replace(
        "tooltip:Object.assign(dashTooltip(),{callbacks:{label:function(c){ return ' '+c.parsed.x+' قطعة'; }}})},",
        "tooltip:Object.assign(dashTooltip(),{callbacks:{label:function(c){ return ' '+c.parsed.x+' '+t('قطعة'); }}})},",
    )

    # Brand + sub in applyChromeI18n
    old_brand = (
        "  var brandName = document.querySelector('.brand-name');\n"
        "  if(brandName) brandName.textContent = t('الفلاحة برو');\n"
    )
    new_brand = (
        "  var brandEl = document.querySelector('.sidebar-logo .brand');\n"
        "  if(brandEl) brandEl.innerHTML = (LANG==='en') ? 'AlFilaha<span> Pro</span>' : 'الفلاحة<span> برو</span>';\n"
        "  var brandSub = document.querySelector('.sidebar-logo .sub');\n"
        "  if(brandSub) brandSub.textContent = t('ERP فلاحي');\n"
    )
    if old_brand in text:
        text = text.replace(old_brand, new_brand, 1)
    elif "sidebar-logo .brand" not in text:
        # insert after season label block
        anchor = "  var seasonLabel = document.querySelector('.sidebar-season label');\n"
        if anchor in text and "sidebar-logo .brand" not in text:
            text = text.replace(
                anchor,
                new_brand + anchor,
                1,
            )

    # Prefer phaseLabel wherever phase.ar is shown in dashboards/tables later if simple
    text = text.replace(
        "return ph.ar;",
        "return phaseLabel(ph);",
    )
    # careful - might break comments; check count. Only in JS returns is fine for phases.

    HTML.write_text(text, encoding="utf-8", newline="\n")
    out = HTML.read_text(encoding="utf-8")
    assert "cropLabel(" in out
    assert "phaseLabel(" in out
    assert "en:'Tomato'" in out
    assert "Click a column to open the plot" in out
    print(f"patched {HTML} ({HTML.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
