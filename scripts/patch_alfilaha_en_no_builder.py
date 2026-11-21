# -*- coding: utf-8 -*-
"""Remove greenhouse builder and add EN/AR bilingual UI to AlFilaha SPA."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "apps" / "alfilaha" / "index.html"

from alfilaha_en_extra import EXTRA_EN  # noqa: E402

EN = {
    "الفلاحة برو": "AlFilaha Pro",
    "الفلاحة برو — نظام تدبير الضيعات الفلاحية": "AlFilaha Pro — Farm Management System",
    "نظام تدبير الضيعات الفلاحية — المغرب": "Farm management system — Morocco",
    "مرحباً بك 🌱": "Welcome back 🌱",
    "ولوج إلى نظام تسيير المزرعة والإنتاج": "Sign in to the farm and production system",
    "البريد الإلكتروني": "Email",
    "الرمز السري (PIN)": "PIN code",
    "تذكّرني على هذا الجهاز": "Remember me on this device",
    "تسجيل الدخول": "Sign in",
    "حسابات تجريبية:": "Demo accounts:",
    "ولوج فوري بنقرة واحدة": "Instant one-click sign-in",
    "مدير الضيعة": "Farm manager",
    "عامل (قراءة فقط)": "Worker (read-only)",
    "© 2026 الفلاحة برو · أكادير، المغرب — الإصدار 1.0": "© 2026 AlFilaha Pro · Agadir, Morocco — v1.0",
    "لوحة القيادة": "Dashboard",
    "القطع الأرضية": "Plots",
    "البيوت البلاستيكية": "Greenhouses",
    "الأراضي المفتوحة": "Open fields",
    "جميع القطع": "All plots",
    "التسيير": "Operations",
    "الأدوية والأسمدة": "Inputs & fertilizers",
    "التقارير": "Reports",
    "النظام": "System",
    "الإعدادات والنسخ": "Settings & backup",
    "الإعدادات والنسخ الاحتياطي": "Settings & backup",
    "المساعدة": "Help",
    "دليل الاستعمال": "User guide",
    "الموسم الفلاحي": "Crop season",
    "طباعة": "Print",
    "خروج": "Sign out",
    "قطعة جديدة": "New plot",
    "حفظ القطعة": "Save plot",
    "إلغاء": "Cancel",
    "تأكيد": "Confirm",
    "تفصيل القطعة": "Plot details",
    "لا حصاد بعد": "No harvest yet",
    "مربح": "Profitable",
    "هامش ضعيف": "Thin margin",
    "خسارة": "Loss",
    "مؤشرات الأداء": "Performance indicators",
    "ربح المتر المربع": "Profit per m²",
    "تكلفة الإنتاج/كغ": "Production cost / kg",
    "متوسط سعر البيع/كغ": "Avg selling price / kg",
    "إجمالي المحصول": "Total harvest",
    "نسبة استرداد التكلفة": "Cost recovery ratio",
    "التكلفة مقابل الإيراد لكل قطعة": "Cost vs revenue per plot",
    "القطع حسب المرحلة": "Plots by stage",
    "توزيع الإيرادات حسب المحصول": "Revenue by crop",
    "ترتيب القطع حسب الربح": "Plots ranked by profit",
    "انقر على أي صف لعرض التفاصيل": "Click any row for details",
    "التكلفة": "Cost",
    "الإيراد": "Revenue",
    "الربح": "Profit",
    "الربحية": "Profitability",
    "القطعة": "Plot",
    "النوع": "Type",
    "المرحلة": "Stage",
    "المحصول": "Crop",
    "المساحة": "Area",
    "الحالة": "Status",
    "إضافة قطعة": "Add plot",
    "بحث": "Search",
    "بيت بلاستيكي": "Greenhouse",
    "أرض مفتوحة": "Open field",
    "حفظ": "Save",
    "تعديل": "Edit",
    "حذف": "Delete",
    "تصدير": "Export",
    "استيراد": "Import",
    "نسخ احتياطي": "Backup",
    "استعادة": "Restore",
    "نعم": "Yes",
    "لا": "No",
    "إضافة تكلفة": "Add cost",
    "إضافة حصاد": "Add harvest",
    "المخزون": "Inventory",
    "الكمية": "Quantity",
    "الوحدة": "Unit",
    "السعر": "Price",
    "التاريخ": "Date",
    "ملاحظات": "Notes",
    "الاسم": "Name",
    "الوصف": "Description",
    "الإجراءات": "Actions",
    "لا توجد بيانات": "No data",
    "درهم": "MAD",
    "كغ": "kg",
    "النمو": "Growth",
    "الحصاد": "Harvest",
    "الإنشاء": "Setup",
    "الزراعة": "Planting",
    "التفكيك": "Dismantling",
    "طماطم": "Tomato",
    "فلفل": "Pepper",
    "فراولة": "Strawberry",
    "خيار": "Cucumber",
    "دليل سريع لاستعمال نظام الفلاحة برو.": "Quick guide to using AlFilaha Pro.",
    "تم إنشاء الموسم": "Season created",
    "وثيقة صادرة عن نظام الفلاحة برو": "Document issued by AlFilaha Pro",
    "خريف": "Autumn",
    "ربيع": "Spring",
    "صيف": "Summer",
    "شتاء": "Winter",
    "الموسم": "Season",
    "اسم الموسم": "Season name",
    "اسم الموسم *": "Season name *",
    "إنشاء موسم": "Create season",
    "مستخدم": "User",
    "الصلاحيات": "Permissions",
    "قراءة فقط": "Read-only",
    "مدير": "Manager",
    "عامل": "Worker",
    "إغلاق": "Close",
    "التالي": "Next",
    "السابق": "Previous",
    "تصفية": "Filter",
    "الكل": "All",
    "نشط": "Active",
    "موقوف": "Inactive",
    "تفاصيل": "Details",
    "العودة": "Back",
    "تحميل": "Download",
    "رفع ملف": "Upload file",
    "نجاح": "Success",
    "تحذير": "Warning",
    "معلومة": "Info",
    "البريد أو الرمز غير صحيح": "Incorrect email or PIN",
    "يجب إدخال البريد والرمز": "Email and PIN are required",
    "تم حفظ البيانات": "Data saved",
    "تم الحذف": "Deleted",
    "تأكيد الحذف": "Confirm delete",
    "هل أنت متأكد؟": "Are you sure?",
    "لا يمكن التراجع عن هذا الإجراء": "This action cannot be undone",
    "التراجع": "Undo",
    "تم التراجع": "Undone",
    "اللغة": "Language",
    "العربية": "Arabic",
    "الإنجليزية": "English",
    "قطع نشطة": "Active plots",
    "المساحة الكلية": "Total area",
    "إجمالي التكاليف": "Total costs",
    "إجمالي الإيرادات": "Total revenue",
    "صافي الربح": "Net profit",
    "هامش الربح": "Profit margin",
    "مزروعة": "planted",
    "بيوت": "greenhouses",
    "حقول": "fields",
    "قطع": "plots",
    "تنبيه المخزون": "Stock alert",
    "مادة بلغت أو تجاوزت حدّ التنبيه": "item(s) at or above alert threshold",
    "نظرة شاملة على موسم": "Overview of season",
    "المؤشرات المالية والإنتاجية لكل ضيعتك": "financial and production indicators for your farm",
    "إضافة مادة": "Add item",
    "حدّ التنبيه": "Alert threshold",
    "الرصيد": "Balance",
    "مصروف": "Expense",
    "إيراد": "Income",
    "تقرير الموسم": "Season report",
    "تقرير الربحية": "Profitability report",
    "ملخص مالي": "Financial summary",
    "التكاليف حسب النوع": "Costs by type",
    "المحاصيل": "Crops",
    "المهام": "Tasks",
    "الآفات": "Pests",
    "مراحل النمو": "Growth stages",
    "بيانات القطعة": "Plot data",
    "سجل التكاليف": "Cost log",
    "سجل الحصاد": "Harvest log",
    "سعر الوحدة": "Unit price",
    "المجموع": "Total",
    "صنف": "Grade",
    "كمية (كغ)": "Quantity (kg)",
    "تاريخ الحصاد": "Harvest date",
    "تاريخ التكلفة": "Cost date",
    "نوع التكلفة": "Cost type",
    "بذور": "Seeds",
    "سماد": "Fertilizer",
    "مبيد": "Pesticide",
    "يد عاملة": "Labor",
    "ماء": "Water",
    "كهرباء": "Electricity",
    "نقل": "Transport",
    "أخرى": "Other",
    "بلاستيك": "Plastic",
    "هيكل": "Structure",
    "ري": "Irrigation",
    "صيانة": "Maintenance",
    "تسويق": "Marketing",
    "تعبئة": "Packaging",
    "ضريبة": "Tax",
    "إيجار": "Rent",
    "تأمين": "Insurance",
    "أدوات": "Tools",
    "وقود": "Fuel",
    "اشتراكات": "Subscriptions",
    "خدمات": "Services",
    "مبيعات": "Sales",
    "زبون": "Customer",
    "قناة البيع": "Sales channel",
    "سوق": "Market",
    "تصدير خارجي": "Export channel",
    "محلي": "Local",
    "جملة": "Wholesale",
    "تقسيط": "Retail",
    "مزارع": "Farmer",
    "ضيعة": "Farm",
    "أكادير": "Agadir",
    "المغرب": "Morocco",
    "درهم مغربي": "Moroccan Dirham",
    "لا توجد قطع في هذا الموسم": "No plots in this season",
    "أضف أول قطعة للبدء": "Add your first plot to get started",
    "عرض الكل": "View all",
    "تحديث": "Refresh",
    "إعدادات عامة": "General settings",
    "المستخدمون": "Users",
    "سجل التدقيق": "Audit log",
    "خطر": "Danger",
    "مسح البيانات": "Clear data",
    "إعادة تعيين": "Reset",
    "نسخة احتياطية JSON": "JSON backup",
    "استيراد نسخة": "Import backup",
    "تنزيل النسخة": "Download backup",
    "اللغة / Language": "Language / اللغة",
}
EN.update(EXTRA_EN)


def remove_builder(text: str) -> str:
    text = re.sub(
        r"/\* ═+\n\s*حاسبة بناء البيوت البلاستيكية — أنماط خاصة.*?@media\(max-width:520px\)\{\n\s*\.build-kpi-grid\{grid-template-columns:1fr\}\n\}\n\n",
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'\s*<span class="nav-section">التخطيط والبناء</span>\s*'
        r'<div class="nav-item" data-page="builder">.*?</div>\n',
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"\s*<!-- حاسبة بناء البيوت -->\s*<div class=\"page\" id=\"page-builder\"></div>\n",
        "\n",
        text,
        count=1,
    )
    text = re.sub(
        r'<div class="modal-backdrop" id="modal-build-link">.*?</div>\n</div>\n\n',
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = text.replace("  builder:'حاسبة بناء البيوت البلاستيكية',\n", "")
    text = text.replace("    case 'builder':   renderBuilder(); break;\n", "")
    text = re.sub(
        r"\n/\* ═+\n\s*حاسبة بناء البيوت البلاستيكية — وحدة مدمجة.*?function bootBuilder\(\)\{.*?\}\n\n",
        "\n\n",
        text,
        count=1,
        flags=re.S,
    )
    text = text.replace("  // ── حاسبة البناء ──\n  bootBuilder();\n\n", "")
    return text


LANG_CSS = """
/* Language direction helpers */
body.lang-en .nav-item{border-right:none;border-left:3px solid transparent}
body.lang-en .nav-item.active{border-left-color:var(--c-leaf)}
body.lang-en .nav-item .badge-count{margin-right:0;margin-left:auto}
body.lang-en .sidebar{text-align:left}
.lang-toggle{
  border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.08);color:#fff;
  border-radius:8px;padding:6px 12px;font-weight:700;font-size:12px;cursor:pointer;font-family:inherit;
}
.lang-toggle:hover{background:rgba(255,255,255,.16)}
.login-lang-wrap{display:flex;justify-content:flex-end;margin-bottom:10px}
.login-lang-wrap .lang-toggle{border-color:var(--c-border);background:var(--c-bg);color:var(--c-text)}
#lang-toggle-app{border-color:var(--c-border);background:var(--c-white);color:var(--c-text)}
"""

I18N_JS_TEMPLATE = r'''
/* ─── Bilingual EN/AR ─────────────────────────────────────── */
var LANG_KEY = 'alfilaha_lang';
var LANG = localStorage.getItem(LANG_KEY) || 'ar';
var I18N_EN = __I18N_EN_JSON__;
var I18N_KEYS = Object.keys(I18N_EN).sort(function(a,b){ return b.length - a.length; });

function t(ar){
  if(LANG !== 'en' || ar == null) return ar;
  var s = String(ar);
  if(I18N_EN[s]) return I18N_EN[s];
  var out = s;
  for(var i=0;i<I18N_KEYS.length;i++){
    var k = I18N_KEYS[i];
    if(k && out.indexOf(k) !== -1) out = out.split(k).join(I18N_EN[k]);
  }
  return out;
}

function translateTextNodeValue(val){
  if(!val || LANG !== 'en') return val;
  var trimmed = val.replace(/\s+/g,' ').trim();
  if(!trimmed) return val;
  if(I18N_EN[trimmed]) {
    return val.replace(trimmed, I18N_EN[trimmed]);
  }
  return t(val);
}

function localizeTree(root){
  if(LANG !== 'en' || !root) return;
  var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
  var node;
  while((node = walker.nextNode())){
    if(!node.parentElement) continue;
    var tag = node.parentElement.tagName;
    if(tag === 'SCRIPT' || tag === 'STYLE' || tag === 'TEXTAREA') continue;
    var next = translateTextNodeValue(node.nodeValue);
    if(next !== node.nodeValue) node.nodeValue = next;
  }
  root.querySelectorAll('[placeholder]').forEach(function(el){
    el.setAttribute('placeholder', t(el.getAttribute('placeholder')));
  });
  root.querySelectorAll('[title]').forEach(function(el){
    el.setAttribute('title', t(el.getAttribute('title')));
  });
}

function setLang(lang){
  LANG = (lang === 'en') ? 'en' : 'ar';
  localStorage.setItem(LANG_KEY, LANG);
  applyDocumentLang();
  try{
    var app = document.getElementById('app-page');
    var login = document.getElementById('login-page');
    if(app && app.style.display !== 'none' && login && login.style.display === 'none'){
      applyChromeI18n();
      if(typeof renderPage === 'function' && typeof currentPage === 'string') renderPage(currentPage);
      if(typeof updateNavCounts === 'function') updateNavCounts();
      localizeTree(document.getElementById('sidebar'));
      localizeTree(document.querySelector('.topbar'));
      localizeTree(document.querySelector('.content'));
    } else {
      // Force a soft refresh of login labels from original Arabic markup by reload
      location.reload();
    }
  }catch(e){ console.warn(e); }
}

function applyDocumentLang(){
  document.documentElement.lang = LANG;
  document.documentElement.dir = (LANG === 'en') ? 'ltr' : 'rtl';
  document.title = t('الفلاحة برو — نظام تدبير الضيعات الفلاحية');
  document.body.classList.toggle('lang-en', LANG === 'en');
  document.body.classList.toggle('lang-ar', LANG !== 'en');
  var a = document.getElementById('lang-toggle-login');
  var b = document.getElementById('lang-toggle-app');
  var label = (LANG === 'en') ? 'العربية' : 'English';
  if(a) a.textContent = label;
  if(b) b.textContent = label;
}

function applyChromeI18n(){
  var nav = {
    dashboard: 'لوحة القيادة',
    serres: 'البيوت البلاستيكية',
    champs: 'الأراضي المفتوحة',
    all: 'جميع القطع',
    inventory: 'الأدوية والأسمدة',
    reports: 'التقارير',
    settings: 'الإعدادات والنسخ',
    help: 'المساعدة'
  };
  Object.keys(nav).forEach(function(page){
    var item = document.querySelector('.nav-item[data-page="'+page+'"]');
    if(!item) return;
    var svg = item.querySelector('svg');
    var badge = item.querySelector('.badge-count');
    item.textContent = '';
    if(svg) item.appendChild(svg);
    item.appendChild(document.createTextNode(' ' + t(nav[page]) + ' '));
    if(badge) item.appendChild(badge);
  });
  var sections = document.querySelectorAll('.nav-section');
  var sectionLabels = ['عام', 'القطع الأرضية', 'التسيير', 'النظام'];
  sections.forEach(function(el, idx){
    if(sectionLabels[idx]) el.textContent = t(sectionLabels[idx]);
  });
  var seasonLabel = document.querySelector('.sidebar-season label');
  if(seasonLabel) seasonLabel.textContent = t('الموسم الفلاحي');
  var brandName = document.querySelector('.brand-name');
  if(brandName) brandName.textContent = t('الفلاحة برو');
  var printBtn = document.getElementById('btn-print-current');
  if(printBtn) printBtn.title = t('طباعة');
  var logoutBtn = document.getElementById('btn-logout');
  if(logoutBtn) logoutBtn.title = t('خروج');
  if(typeof PAGE_TITLES !== 'undefined' && typeof currentPage === 'string'){
    var title = document.getElementById('page-title');
    if(title) title.textContent = t(PAGE_TITLES[currentPage] || '');
  }
}

function wireLangToggles(){
  function flip(){ setLang(LANG === 'en' ? 'ar' : 'en'); }
  var a = document.getElementById('lang-toggle-login');
  var b = document.getElementById('lang-toggle-app');
  if(a) a.onclick = flip;
  if(b) b.onclick = flip;
}

function localizeLogin(){
  localizeTree(document.getElementById('login-page'));
}
'''


def inject_i18n(text: str) -> str:
    text = text.replace("</style>", LANG_CSS + "\n</style>", 1)
    text = text.replace(
        '<div class="login-box">',
        '<div class="login-box">\n'
        '    <div class="login-lang-wrap"><button type="button" class="lang-toggle" id="lang-toggle-login">English</button></div>',
        1,
    )
    text = text.replace(
        '<div class="topbar-right">\n        <button class="btn btn-ghost btn-icon" id="btn-print-current"',
        '<div class="topbar-right">\n'
        '        <button type="button" class="lang-toggle" id="lang-toggle-app">English</button>\n'
        '        <button class="btn btn-ghost btn-icon" id="btn-print-current"',
        1,
    )

    i18n_js = I18N_JS_TEMPLATE.replace("__I18N_EN_JSON__", json.dumps(EN, ensure_ascii=False))
    marker = "   الفلاحة برو — منطق التطبيق"
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit("app logic marker not found")
    insert_at = text.find("\n", text.find("*/", idx)) + 1
    text = text[:insert_at] + "\n" + i18n_js + "\n" + text[insert_at:]

    text = text.replace(
        "document.getElementById('page-title').textContent = PAGE_TITLES[page]||'';",
        "document.getElementById('page-title').textContent = t(PAGE_TITLES[page]||'');",
    )

    # After each page render, localize the active page DOM
    text = text.replace(
        "function renderPage(page){\n  switch(page){",
        "function renderPage(page){\n  switch(page){",
        1,
    )
    text = re.sub(
        r"(function renderPage\(page\)\{\n  switch\(page\)\{.*?\n  \}\n)(\})",
        r"\1  var pageEl = document.getElementById('page-'+page);\n"
        r"  if(pageEl) localizeTree(pageEl);\n"
        r"  localizeTree(document.querySelector('.topbar'));\n"
        r"\2",
        text,
        count=1,
        flags=re.S,
    )

    text = re.sub(
        r"(function toast\(msg(?:,\s*\w+)?\)\{\n)",
        r"\1  msg = t(msg);\n",
        text,
        count=1,
    )

    text = text.replace(
        "function boot(){",
        "function boot(){\n"
        "  applyDocumentLang();\n"
        "  wireLangToggles();\n"
        "  localizeLogin();\n",
        1,
    )

    text = re.sub(
        r"function enterApp\(([^)]*)\)\{\n",
        r"function enterApp(\1){\n  applyChromeI18n();\n",
        text,
        count=1,
    )

    # Localize open modals content when opened — patch openModal
    text = re.sub(
        r"function openModal\(id\)\{ document\.getElementById\(id\)\.classList\.add\('open'\); \}",
        "function openModal(id){ var m=document.getElementById(id); m.classList.add('open'); localizeTree(m); }",
        text,
        count=1,
    )
    return text


def simplify_farm_manager_login(text: str) -> str:
    """Keep a single farm-manager account; remove worker/staff login."""
    # Allow longer passwords (API-aligned Manager123!)
    text = text.replace(
        'id="l-pass" placeholder="••••" autocomplete="current-password" maxlength="8"',
        'id="l-pass" placeholder="••••" autocomplete="current-password" maxlength="64"',
    )
    # Demo UI: farm manager only
    text = re.sub(
        r'<div class="demo-accounts">\s*'
        r'<button class="btn-demo" id="btn-demo-admin">👨‍🌾 مدير الضيعة</button>\s*'
        r'<button class="btn-demo staff" id="btn-demo-staff">👤 عامل \(قراءة فقط\)</button>\s*'
        r"</div>",
        '<div class="demo-accounts">\n'
        '        <button class="btn-demo" id="btn-demo-admin">👨‍🌾 مدير الضيعة</button>\n'
        "      </div>",
        text,
        count=1,
    )
    # Single user aligned with API seed manager
    text = re.sub(
        r"var USERS = \[\s*"
        r"\{email:'admin@filaha\.ma', name:'مدير الضيعة', role:'admin',\s*"
        r"pinHash:simpleHash\('2026'\), initials:'م'\},\s*"
        r"\{email:'amine@filaha\.ma', name:'أمين العمري', role:'staff',\s*"
        r"pinHash:simpleHash\('1234'\), initials:'أ'\}\s*"
        r"\];",
        "var USERS = [\n"
        "  {email:'manager@farm.ma', name:'Farm Manager', nameAr:'مدير الضيعة', role:'admin',\n"
        "   pinHash:simpleHash('Manager123!'), initials:'M'}\n"
        "];",
        text,
        count=1,
    )
    # Role label prefers localized farm manager
    text = text.replace(
        "currentUser.role==='admin' ? 'مدير الضيعة' : 'عامل — قراءة فقط';",
        "currentUser.role==='admin'\n"
        "      ? (LANG==='en' ? 'Farm manager' : (currentUser.nameAr||'مدير الضيعة'))\n"
        "      : (LANG==='en' ? 'Worker — read-only' : 'عامل — قراءة فقط');",
    )
    # Demo click + remove staff handler
    text = text.replace(
        "document.getElementById('btn-demo-admin').addEventListener('click',function(){\n"
        "    doLogin('admin@filaha.ma','2026',true);\n"
        "  });\n"
        "  document.getElementById('btn-demo-staff').addEventListener('click',function(){\n"
        "    doLogin('amine@filaha.ma','1234',true);\n"
        "  });",
        "document.getElementById('btn-demo-admin').addEventListener('click',function(){\n"
        "    doLogin('manager@farm.ma','Manager123!',true);\n"
        "  });",
    )
    # Reject stale non-manager sessions
    text = text.replace(
        "function loadSession(){\n"
        "  try{\n"
        "    var raw = sessionStorage.getItem(SESSION_KEY) || localStorage.getItem(SESSION_KEY);\n"
        "    if(raw){ currentUser = JSON.parse(raw); return true; }\n"
        "  }catch(e){}\n"
        "  return false;\n"
        "}",
        "function loadSession(){\n"
        "  try{\n"
        "    var raw = sessionStorage.getItem(SESSION_KEY) || localStorage.getItem(SESSION_KEY);\n"
        "    if(raw){\n"
        "      var u = JSON.parse(raw);\n"
        "      // Farm-manager-only login: drop legacy staff sessions\n"
        "      if(!u || u.role!=='admin' || (u.email && u.email!=='manager@farm.ma' && u.email!=='admin@filaha.ma')){\n"
        "        clearSession(); return false;\n"
        "      }\n"
        "      // Migrate legacy admin email to manager@farm.ma\n"
        "      if(u.email==='admin@filaha.ma'){\n"
        "        u.email='manager@farm.ma'; u.name='Farm Manager'; u.nameAr='مدير الضيعة'; u.initials='M';\n"
        "      }\n"
        "      currentUser = u; return true;\n"
        "    }\n"
        "  }catch(e){}\n"
        "  return false;\n"
        "}",
    )
    # Placeholder email hint
    text = text.replace(
        'id="l-email" placeholder="example@filaha.ma"',
        'id="l-email" placeholder="manager@farm.ma"',
    )
    # Pre-fill manager credentials for clearer demo login
    text = text.replace(
        "  localizeLogin();\n\n  loadDB();",
        "  localizeLogin();\n\n  loadDB();\n"
        "  var emailEl = document.getElementById('l-email');\n"
        "  var passEl = document.getElementById('l-pass');\n"
        "  if(emailEl && !emailEl.value) emailEl.value = 'manager@farm.ma';\n"
        "  if(passEl && !passEl.value) passEl.value = 'Manager123!';",
    )
    text = text.replace(
        "function doLogout(){\n"
        "  clearSession();\n"
        "  document.getElementById('app-page').style.display = 'none';\n"
        "  document.getElementById('login-page').style.display = 'flex';\n"
        "  document.getElementById('l-email').value = '';\n"
        "  document.getElementById('l-pass').value = '';\n"
        "}",
        "function doLogout(){\n"
        "  clearSession();\n"
        "  document.getElementById('app-page').style.display = 'none';\n"
        "  document.getElementById('login-page').style.display = 'flex';\n"
        "  document.getElementById('l-email').value = 'manager@farm.ma';\n"
        "  document.getElementById('l-pass').value = 'Manager123!';\n"
        "  localizeLogin();\n"
        "}",
    )
    return text


def main() -> None:
    # Always start from clean prototype + fonts
    import subprocess
    import sys

    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "install_alfilaha_frontend.py")])
    text = HTML.read_text(encoding="utf-8")
    text = remove_builder(text)
    for banned in ("page-builder", "renderBuilder", "bootBuilder", "التخطيط والبناء", "modal-build-link"):
        if banned in text:
            raise SystemExit(f"builder remnant remains: {banned}")
    text = inject_i18n(text)
    text = simplify_farm_manager_login(text)
    HTML.write_text(text, encoding="utf-8", newline="\n")
    out = HTML.read_text(encoding="utf-8")
    assert "setLang" in out and "lang-toggle-app" in out
    assert "page-builder" not in out
    assert "manager@farm.ma" in out
    assert "btn-demo-staff" not in out
    assert "amine@filaha.ma" not in out
    print(f"patched {HTML} ({HTML.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
