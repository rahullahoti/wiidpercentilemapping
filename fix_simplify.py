#!/usr/bin/env python3
"""Remove SVG download, fix PNG filename, reduce label density."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('inequalitymatrix.html', 'r', encoding='utf-8') as f:
    html = f.read()

def apply(desc, old, new):
    assert old in html, f'NOT FOUND: {desc}\n  -> {old[:100]}'
    result = html.replace(old, new, 1)
    assert result != html, f'No change: {desc}'
    print(f'OK  {desc}')
    return result

# S1. Remove SVG button — revert to single "⬇ Download" button
html = apply('S1 remove SVG button',
    '<button class="zoom-btn download-btn" id="downloadBtn" title="Save chart as PNG (print-ready, 4800×3900 px)">⬇ PNG</button>'
    '<button class="zoom-btn download-btn" id="downloadSVGBtn" title="Save chart as SVG (vector, scalable)" style="margin-left:4px">⬇ SVG</button>',
    '<button class="zoom-btn download-btn" id="downloadBtn" title="Save chart as PNG (print-ready, 4800×3900 px)">⬇ Download</button>')

# S2. Restore .png in fileName (fix PNG download)
html = apply('S2 restore .png in fileName',
    ".replace(/[<>:\"/\\\\|?*]/g, '_');",
    ".replace(/[<>:\"/\\\\|?*]/g, '_') + '.png';")

# S3. Remove the .png appended at a.download (Fix2b — now double .png.png)
html = apply('S3 remove double .png at a.download',
    "a.download = fileName + '.png';",
    "a.download = fileName;")

# S4. Remove SVG format branch from downloadChart
OLD_SVG_BRANCH = (
    "\n  // SVG direct download branch\n"
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
    "  }\n"
)
html = apply('S4 remove SVG format branch', OLD_SVG_BRANCH, '\n')

# S5. Remove format parameter from downloadChart signature
html = apply('S5 remove format param from downloadChart',
    "function downloadChart(exportFilename, format = 'png') {",
    "function downloadChart(exportFilename) {")

# S6. Remove SVG button event handler
OLD_SVG_HANDLER = (
    "  document.getElementById('downloadSVGBtn').addEventListener('click', () => {\n"
    "    const svgBtn = document.getElementById('downloadSVGBtn');\n"
    "    if (svgBtn.disabled) return;\n"
    "    svgBtn.disabled = true; svgBtn.textContent = '⏳';\n"
    "    downloadChart(`inequality-${S.baseYear}-${S.finalYear}`, 'svg');\n"
    "    setTimeout(() => { svgBtn.disabled = false; svgBtn.textContent = '⬇ SVG'; }, 2500);\n"
    "  });"
)
html = apply('S6 remove SVG button handler', OLD_SVG_HANDLER, '')

# S7. Reduce maxLabels 100 -> 45 (collision detection handles the rest)
html = apply('S7 maxLabels 100->45',
    'const maxLabels = Math.min(100, data.length);',
    'const maxLabels = Math.min(45, data.length);')

# S8. Increase label bounding box padding for better collision avoidance
html = apply('S8 label bbox padding',
    'let box = { x:lx-1, y:ly-lh, w:lw+2, h:lh+2 };',
    'let box = { x:lx-4, y:ly-lh-5, w:lw+8, h:lh+10 };')

# S9. Also update the second box assignment (left-side attempt)
html = apply('S9 label bbox padding left side',
    'box = { x:lx-1, y:ly-lh, w:lw+2, h:lh+2 };',
    'box = { x:lx-4, y:ly-lh-5, w:lw+8, h:lh+10 };')

with open('inequalitymatrix.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('\nAll simplification changes applied.')
