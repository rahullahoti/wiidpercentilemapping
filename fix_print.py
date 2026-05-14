#!/usr/bin/env python3
"""Apply print-quality improvements to inequalitymatrix.html.

Changes:
 P1.  EH 1000->1300, titleH 85->175, padX 80->100, padR 50->60
 P2.  legendH 130/80 -> 280/180, sourceH 52->80
 P3.  Title: y=38 font-24 -> y=65 font-53
 P4.  metaY start: 62->130, branch: 80->165
 P5.  Filter text font 13->29
 P6.  Replace meta/subtitle with descriptive dynamic text
 P7.  Threshold lines: dasharray 6,4->13,9; stroke-width 1.2->2.5
 P8.  Threshold label fonts: 9.5->21, 9->20
 P9.  Grid x-tick: y-offset +18->+38, font 12->26
 P10. Grid y-tick: x="-14"->"-18", font 12->26
 P11. X-axis label: y-offset +38->+78, font 12->26
 P12. Y-axis label: translate(-54)->translate(-70), font 14->31
 P13. Label charW: 6.5/5.5 -> 14.3/12.1
 P14. Label fs: '16'/'14' -> '35'/'31'; halo stroke-width 3.5->8
 P15. Region legend: font 11->24, spacing 62->140
 P16. Region legend item: font 12->26, spacing formula
 P17. Size legend: y-offset 32->65, font 11->24, slx-start 88->200
 P18. Size legend bubbles: cap 26->40, font 9->20
 P19. Size legend item spacing: max(r*2+16,55) -> max(r*2+28,80)
 P20. Footer note: font 10->22, y EH-36->EH-55
 P21. Matrix legend Y positions: +76->+170, +44->+110
 P22. Matrix legend sizes: cw 15->33, ch 13->29, gap 4->9
 P23. Matrix legend header font 11.5->25; column spacing 145+ti*105 -> 145+ti*195
 P24. Matrix legend item font 11->24; x offsets scaled
 P25. Matrix legend level font 10.5->23; x offset scaled
 P26. Source lines: y EH-20->EH-25, font 11.5->25, fill darkened
 P27. Add SVG download: refactor downloadChart to accept format param
 P28. Add SVG download button to HTML
"""
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

# ── P1. Canvas height + layout constants ────────────────────────────────────
html = apply('P1 EH 1000->1300',
    'const EW = 1600, EH = 1000;',
    'const EW = 1600, EH = 1300;')

html = apply('P1 padX/padR/titleH',
    'const padX = 80, padR = 50, titleH = 85;',
    'const padX = 100, padR = 60, titleH = 175;')

# ── P2. Legend and source heights ───────────────────────────────────────────
html = apply('P2 legendH 130/80 -> 280/180',
    'const legendH = S.sizeBy !== \'none\' ? 130 : 80;',
    'const legendH = S.sizeBy !== \'none\' ? 280 : 180;')

html = apply('P2 sourceH 52->80',
    'const sourceH = 52;',
    'const sourceH = 80;')

# ── P3. Title position and size ─────────────────────────────────────────────
html = apply('P3 title y/font',
    'y="38" font-family="Georgia,serif" font-size="24" font-weight="700" fill="#222220"',
    'y="65" font-family="Georgia,serif" font-size="53" font-weight="700" fill="#222220"')

# ── P4. metaY starting values ───────────────────────────────────────────────
html = apply('P4 metaY init 62->130',
    'let metaY = 62;',
    'let metaY = 130;')

html = apply('P4 metaY branch 80->165',
    'metaY = 80;',
    'metaY = 165;')

# ── P5. Filter text font ────────────────────────────────────────────────────
html = apply('P5 filter font 13->29',
    'font-size="13" fill="#888882">${escXml(filters.join(',
    'font-size="29" fill="#888882">${escXml(filters.join(')

# ── P6. Descriptive subtitle (replaces raw "N countries · Bubble = X") ─────
OLD_META = (
    's.push(`<text x="${padX}" y="${metaY}" font-family="sans-serif" '
    'font-size="12" fill="#ABAAA2">${escXml(data.length + \' countries \\u00B7 Bubble = \' + '
    '(S.sizeBy === \'none\' ? \'uniform\' : S.sizeBy))}</text>`);'
)
NEW_META = (
    'const bubbleDesc = S.sizeBy === \'population\' ? \'Bubble size ∝ 2022 population.\' '
    ': S.sizeBy === \'gdp\' ? \'Bubble size ∝ GDP per capita.\' : \'Uniform bubble size.\';\n'
    '  s.push(`<text x="${padX}" y="${metaY}" font-family="sans-serif" '
    'font-size="26" fill="#888882">${escXml(data.length + \' countries · \' + bubbleDesc + \' Colour = World Bank region.\')}</text>`);'
)
html = apply('P6 descriptive subtitle', OLD_META, NEW_META)

# ── P7. Threshold lines ──────────────────────────────────────────────────────
html = apply('P7 threshold line stroke',
    'stroke-dasharray="6,4" stroke-width="1.2"/>`);',
    'stroke-dasharray="13,9" stroke-width="2.5"/>`);')

# ── P8. Threshold label fonts ────────────────────────────────────────────────
html = apply('P8 threshold Gini label 9.5->21',
    'font-size="9.5" fill="#888882" text-anchor="start">Gini',
    'font-size="21" fill="#888882" text-anchor="start">Gini')

html = apply('P8 threshold No-change label 9.5->21',
    'font-size="9.5" fill="#888882" text-anchor="end">No change',
    'font-size="21" fill="#888882" text-anchor="end">No change')

# Two stalled-band labels share font-size="9" — replace both
html = html.replace(
    'font-size="9" fill="#aaa" text-anchor="end">',
    'font-size="20" fill="#aaa" text-anchor="end">')
print('OK  P8 stalled-band label font 9->20')

# ── P9. X-axis tick labels ───────────────────────────────────────────────────
html = apply('P9 x-tick y-offset +18->+38 and font 12->26',
    'y="${chartH+18}" font-family="sans-serif" font-size="12" fill="#555550" text-anchor="middle">${v}</text>`);',
    'y="${chartH+38}" font-family="sans-serif" font-size="26" fill="#555550" text-anchor="middle">${v}</text>`);')

# ── P10. Y-axis tick labels ──────────────────────────────────────────────────
html = apply('P10 y-tick x-offset and font 12->26',
    'x="-14" y="${y+4}" font-family="sans-serif" font-size="12" fill="#555550" text-anchor="end">${v}</text>`);',
    'x="-18" y="${y+4}" font-family="sans-serif" font-size="26" fill="#555550" text-anchor="end">${v}</text>`);')

# ── P11. X-axis axis label ───────────────────────────────────────────────────
html = apply('P11 x-axis label y-offset +38->+78 font 12->26',
    'y="${chartH+38}" font-family="sans-serif" font-size="12" font-weight="500" fill="#555550" text-anchor="middle">Gini index',
    'y="${chartH+78}" font-family="sans-serif" font-size="26" font-weight="500" fill="#555550" text-anchor="middle">Gini index')

# ── P12. Y-axis axis label ───────────────────────────────────────────────────
html = apply('P12 y-axis label translate and font 14->31',
    'translate(-54,${chartH/2}) rotate(-90)"><text font-family="sans-serif" font-size="14" font-weight="600" fill="#444440"',
    'translate(-72,${chartH/2}) rotate(-90)"><text font-family="sans-serif" font-size="31" font-weight="600" fill="#444440"')

# ── P13. Label charW for collision detection ─────────────────────────────────
html = apply('P13 label charW 6.5/5.5->14.3/12.1',
    'const charW = useFull ? 6.5 : 5.5;',
    'const charW = useFull ? 14.3 : 12.1;')

html = apply('P13 label lh 12->31',
    'const lw = text.length * charW, lh = 12;',
    'const lw = text.length * charW, lh = 31;')

# ── P14. Country label font sizes and halo stroke ───────────────────────────
html = apply('P14 label fs 16/14->35/31',
    "const fs = matched ? '16' : '14';",
    "const fs = matched ? '35' : '31';")

html = apply('P14 halo stroke-width 3.5->8',
    'stroke-width="3.5" opacity="${op}">${escXml(text)}</text>`);',
    'stroke-width="8" opacity="${op}">${escXml(text)}</text>`);')

# ── P15. Region legend label font ────────────────────────────────────────────
html = apply('P15 region legend "Regions:" font 11->24 spacing 62->140',
    'font-size="11" font-weight="600" fill="#555550">Regions:</text>`);'
    '\n  legX += 62;',
    'font-size="24" font-weight="600" fill="#555550">Regions:</text>`);'
    '\n  legX += 140;')

# ── P16. Region legend items ─────────────────────────────────────────────────
# dot is already r=7; change to r=15
html = apply('P16 region dot r=7->15',
    """cy="${legY-3.5}" r="7" fill="${REGION_COLORS[r]}"/>`);""",
    """cy="${legY-3.5}" r="15" fill="${REGION_COLORS[r]}"/>`);""")

html = apply('P16 region item font 12->26 and spacing',
    """x="${legX+9}" y="${legY}" font-family="sans-serif" font-size="12" fill="#444">${escXml(REGION_SHORT[r])}</text>`);
    legX += REGION_SHORT[r].length * 6.5 + 24;""",
    """x="${legX+20}" y="${legY}" font-family="sans-serif" font-size="26" fill="#444">${escXml(REGION_SHORT[r])}</text>`);
    legX += REGION_SHORT[r].length * 14 + 44;""")

# ── P17. Size legend Y-offset and label ─────────────────────────────────────
html = apply('P17 size legend y-offset 32->65 font 11->24 slx 88->200',
    'const sizeLegY = legY + 32;\n    let slx = padX;\n'
    '    s.push(`<text x="${slx}" y="${sizeLegY+4}" font-family="sans-serif" '
    'font-size="11" font-weight="600" fill="#555550">',
    'const sizeLegY = legY + 65;\n    let slx = padX;\n'
    '    s.push(`<text x="${slx}" y="${sizeLegY+4}" font-family="sans-serif" '
    'font-size="24" font-weight="600" fill="#555550">')

html = apply('P17 slx start offset 88->200',
    'slx += 88;',
    'slx += 200;')

# ── P18. Size legend bubble cap and tick font ────────────────────────────────
html = apply('P18 size legend bubble cap 26->40',
    'const r = Math.min(rScale(v), 26); // cap radius',
    'const r = Math.min(rScale(v), 40); // cap radius')

html = apply('P18 size legend tick font 9->20',
    'y="${sizeLegY+r+12}" font-family="sans-serif" font-size="9" fill="#888882"',
    'y="${sizeLegY+r+24}" font-family="sans-serif" font-size="20" fill="#888882"')

# ── P19. Size legend item spacing ───────────────────────────────────────────
html = apply('P19 size legend spacing max(r*2+16,55)->max(r*2+36,90)',
    'slx += Math.max(r * 2 + 16, 55);',
    'slx += Math.max(r * 2 + 36, 90);')

# ── P20. Footer note font and position ──────────────────────────────────────
html = apply('P20 footer note font 10->22 y EH-36->EH-55',
    'y="${EH-36}" font-family="sans-serif" font-size="10" fill="#888882">Note:',
    'y="${EH-58}" font-family="sans-serif" font-size="22" fill="#666662">Note:')

# ── P21. Matrix legend Y positions ──────────────────────────────────────────
html = apply('P21 matrix legend Y sizeBy +76->+170',
    'const mlY = S.sizeBy !== \'none\' ? legY + 76 : legY + 44;',
    'const mlY = S.sizeBy !== \'none\' ? legY + 170 : legY + 110;')

# ── P22. Matrix legend cell sizes ───────────────────────────────────────────
html = apply('P22 matrix legend cw/ch/gap 15/13/4 -> 33/29/9',
    'const cw=15, ch=13, gap=4;',
    'const cw=33, ch=29, gap=9;')

# ── P23. Matrix legend header font and column spacing ───────────────────────
html = apply('P23 matrix header font 11.5->25 column spacing',
    'font-size="11.5" font-weight="600" fill="#333">Gini level',
    'font-size="25" font-weight="600" fill="#333">Gini level')

html = apply('P23 matrix trend labels x offset 145+ti*105->145+ti*200 font 11->24',
    '`<text x="${mlX+145+ti*105}" y="${mlY}" font-family="sans-serif" font-size="11" fill="#555">',
    '`<text x="${mlX+145+ti*200}" y="${mlY}" font-family="sans-serif" font-size="24" fill="#555">')

# ── P24. Matrix legend level labels ─────────────────────────────────────────
html = apply('P24 matrix level label x 135->290 font 10.5->23',
    'x="${mlX+135}" y="${ry+ch-2}" font-family="sans-serif" font-size="10.5" fill="#666" text-anchor="end"',
    'x="${mlX+290}" y="${ry+ch-2}" font-family="sans-serif" font-size="23" fill="#666" text-anchor="end"')

# ── P25. Matrix legend cell rects column offsets ────────────────────────────
html = apply('P25 matrix cell rx offset 145+ti*105 -> 300+ti*200',
    'const rx = mlX + 145 + ti*105 - 2;',
    'const rx = mlX + 300 + ti*200 - 2;')

# ── P26. Source lines: font 11.5->25, y EH-20->EH-25, fill darkened ─────────
html = apply('P26 left source font/position',
    'y="${EH-20}" font-family="sans-serif" font-size="11.5" fill="#777772">Source: WIID Companion',
    'y="${EH-25}" font-family="sans-serif" font-size="25" fill="#555552">Source: WIID Companion')

html = apply('P26 right source font/position',
    'y="${EH-20}" font-family="sans-serif" font-size="11.5" fill="#777772" text-anchor="end">Source: WIID Companion',
    'y="${EH-25}" font-family="sans-serif" font-size="25" fill="#555552" text-anchor="end">Source: WIID Companion')

# ── P27. Refactor downloadChart to support SVG format ───────────────────────
# Insert SVG branch right after svgStr is built
SVG_BRANCH_ANCHOR = "  const svgStr = s.join('\\n');\n\n  // --- Render to canvas at 2x DPI ---"
SVG_BRANCH_NEW = (
    "  const svgStr = s.join('\\n');\n\n"
    "  // SVG direct download branch\n"
    "  if (format === 'svg') {\n"
    "    const blob = new Blob([svgStr], {type: 'image/svg+xml'});\n"
    "    const a = document.createElement('a');\n"
    "    a.href = URL.createObjectURL(blob);\n"
    "    a.download = fileName + '.svg';\n"
    "    document.body.appendChild(a);\n"
    "    a.click();\n"
    "    document.body.removeChild(a);\n"
    "    setTimeout(() => URL.revokeObjectURL(a.href), 2000);\n"
    "    resetBtn(true);\n"
    "    return;\n"
    "  }\n\n"
    "  // --- Render to canvas at 2x DPI ---"
)
html = apply('P27 SVG format branch', SVG_BRANCH_ANCHOR, SVG_BRANCH_NEW)

# Add format='png' default param to downloadChart function signature
html = apply('P27 downloadChart format param',
    'function downloadChart(exportFilename) {',
    "function downloadChart(exportFilename, format = 'png') {")

# ── P28. Add SVG download button to HTML ────────────────────────────────────
OLD_BTN = '<button class="zoom-btn download-btn" id="downloadBtn" title="Download chart as image">⬇ Download</button>'
NEW_BTN = (
    '<button class="zoom-btn download-btn" id="downloadBtn" title="Save chart as PNG (print-ready, 4800×3900 px)">⬇ PNG</button>'
    '<button class="zoom-btn download-btn" id="downloadSVGBtn" title="Save chart as SVG (vector, scalable)" style="margin-left:4px">⬇ SVG</button>'
)
html = apply('P28 SVG download button', OLD_BTN, NEW_BTN)

# Add SVG button event handler after existing dlConfirm handler
OLD_HANDLER_END = (
    "  document.getElementById('dlConfirm').addEventListener('click', () => {\n"
    "    dlPop.classList.add('hidden');\n"
    "    downloadChart(dlInput.value.trim() || `inequality-${S.baseYear}-${S.finalYear}`);\n"
    "  });"
)
NEW_HANDLER_END = (
    "  document.getElementById('dlConfirm').addEventListener('click', () => {\n"
    "    dlPop.classList.add('hidden');\n"
    "    downloadChart(dlInput.value.trim() || `inequality-${S.baseYear}-${S.finalYear}`);\n"
    "  });\n"
    "  document.getElementById('downloadSVGBtn').addEventListener('click', () => {\n"
    "    downloadChart(`inequality-${S.baseYear}-${S.finalYear}`, 'svg');\n"
    "  });"
)
html = apply('P28 SVG button event handler', OLD_HANDLER_END, NEW_HANDLER_END)

with open('inequalitymatrix.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('\nAll print-quality changes applied and saved.')
