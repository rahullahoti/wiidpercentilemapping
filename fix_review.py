#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('inequalitymatrix.html', 'r', encoding='utf-8') as f:
    html = f.read()

def apply(desc, old, new):
    assert old in html, f'NOT FOUND: {desc}\n  Looking for: {old[:100]}'
    result = html.replace(old, new, 1)
    assert result != html, f'No change: {desc}'
    print(f'OK  {desc}')
    return result

# Fix 1: high-dec export cell hardcoded color
html = apply('Fix1: high-dec cell color',
    "w:chartW-txH_e,    h:chartH-tyDec_e,           fill:'#e8f2fc' },",
    "w:chartW-txH_e,    h:chartH-tyDec_e,           fill:QUADRANT_DEFS.find(q=>q.id==='high-dec').bg },")

# Fix 2: SVG filename — strip .png from base fileName, add per-format at download
html = apply("Fix2a: remove .png from base fileName",
    ".replace(/[<>:\"/\\\\|?*]/g, '_') + '.png';",
    ".replace(/[<>:\"/\\\\|?*]/g, '_');")

html = apply('Fix2b: add .png at PNG download point',
    "a.download = fileName;",
    "a.download = fileName + '.png';")

# Fix 3: thresholdHigh label font 9.5 -> 21
html = apply('Fix3: thresholdHigh label font 9.5->21',
    'font-size="9.5" fill="#888882" text-anchor="start">Gini ${S.thresholdHigh}',
    'font-size="21" fill="#888882" text-anchor="start">Gini ${S.thresholdHigh}')

# Fix 4: SVG button disabled guard
OLD4 = (
    "document.getElementById('downloadSVGBtn').addEventListener('click', () => {\n"
    "    downloadChart(`inequality-${S.baseYear}-${S.finalYear}`, 'svg');\n"
    "  });"
)
NEW4 = (
    "document.getElementById('downloadSVGBtn').addEventListener('click', () => {\n"
    "    const svgBtn = document.getElementById('downloadSVGBtn');\n"
    "    if (svgBtn.disabled) return;\n"
    "    svgBtn.disabled = true; svgBtn.textContent = '⏳';\n"
    "    downloadChart(`inequality-${S.baseYear}-${S.finalYear}`, 'svg');\n"
    "    setTimeout(() => { svgBtn.disabled = false; svgBtn.textContent = '⬇ SVG'; }, 2500);\n"
    "  });"
)
html = apply('Fix4: SVG button disabled guard', OLD4, NEW4)

with open('inequalitymatrix.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('\nAll fixes applied.')
