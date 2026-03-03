import { chromium } from 'playwright';
import { writeFileSync } from 'fs';

const PAGE_URL = 'file:///c:/Users/rahul.lahoti/Downloads/wiidpercentilemapping/inequalitymatrix.html';
const OUT = (name) => `C:/Users/rahul.lahoti/Downloads/wiidpercentilemapping/review-${name}.png`;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.setViewportSize({ width: 1440, height: 900 });

// STEP 1 — Navigate and wait
console.log('STEP 1: navigating...');
await page.goto(PAGE_URL, { waitUntil: 'networkidle' });
await page.waitForTimeout(3000);
console.log('STEP 1: DONE — page loaded');

// STEP 2 — Full above-fold screenshot
console.log('STEP 2: screenshot above fold...');
await page.screenshot({ path: OUT('step2-abovefold'), clip: { x: 0, y: 0, width: 1440, height: 900 } });
const chartEl = await page.$('svg, canvas, .chart-container, #chart');
console.log('STEP 2: chart element found?', !!chartEl);
if (chartEl) {
  const box = await chartEl.boundingBox();
  console.log('STEP 2: chart bounding box:', JSON.stringify(box));
}

// STEP 3 — Scroll down slightly
console.log('STEP 3: scrolling to see controls + chart together...');
await page.evaluate(() => window.scrollBy(0, 150));
await page.waitForTimeout(500);
await page.screenshot({ path: OUT('step3-controls-chart') });
console.log('STEP 3: screenshot taken');

// STEP 4 — Hover over a bubble/dot
console.log('STEP 4: looking for bubble to hover...');
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForTimeout(300);

// Try to find a circle element in SVG
const circles = await page.$$('svg circle');
console.log('STEP 4: circles found:', circles.length);
let hovered = false;
for (const circle of circles) {
  const box = await circle.boundingBox();
  if (box && box.width > 5) {
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await page.waitForTimeout(800);
    await page.screenshot({ path: OUT('step4-tooltip') });

    // Check tooltip content
    const tooltip = await page.$('.tooltip, [class*="tooltip"], [id*="tooltip"]');
    if (tooltip) {
      const text = await tooltip.innerText().catch(() => '');
      console.log('STEP 4: tooltip text:', JSON.stringify(text));
    } else {
      // Look for any visible tooltip-like element
      const allText = await page.evaluate(() => {
        const els = document.querySelectorAll('[style*="opacity: 1"], [style*="display: block"]');
        return Array.from(els).map(e => e.innerText).filter(t => t.length > 0);
      });
      console.log('STEP 4: visible elements text after hover:', JSON.stringify(allText.slice(0, 3)));
    }
    hovered = true;
    break;
  }
}
if (!hovered) console.log('STEP 4: no suitable circle found');

// STEP 5 — Click Options button
console.log('STEP 5: looking for Options button...');
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForTimeout(300);

const optionsBtn = await page.$('button:has-text("Options"), button:has-text("⚙"), [data-testid="options"]');
if (optionsBtn) {
  await optionsBtn.click();
  await page.waitForTimeout(600);
  await page.screenshot({ path: OUT('step5-options-popover') });

  const popover = await page.$('[class*="popover"], [class*="dropdown"], [class*="options"], [class*="panel"]');
  console.log('STEP 5: popover element found?', !!popover);

  // Check for specific controls
  const pageText = await page.evaluate(() => document.body.innerText);
  const hasXAxis = pageText.includes('X-Axis') || pageText.includes('x-axis') || pageText.includes('X axis');
  const hasThreshold = pageText.includes('Threshold');
  const hasBubbleSize = pageText.includes('Bubble Size') || pageText.includes('bubble size');
  const hasLabels = pageText.includes('Labels');
  console.log('STEP 5: X-Axis:', hasXAxis, 'Threshold:', hasThreshold, 'Bubble Size:', hasBubbleSize, 'Labels:', hasLabels);
} else {
  // Try broader search
  const allButtons = await page.$$('button');
  for (const btn of allButtons) {
    const text = await btn.innerText().catch(() => '');
    console.log('STEP 5: button found:', text.trim());
  }
  await page.screenshot({ path: OUT('step5-options-popover') });
  console.log('STEP 5: Options button NOT found');
}

// STEP 6 — Close options, scroll to bottom of chart area
console.log('STEP 6: closing options and scrolling to chart bottom...');
await page.keyboard.press('Escape');
await page.waitForTimeout(300);

// Find the SVG/chart and scroll to show its bottom
const svgEl = await page.$('svg');
if (svgEl) {
  const box = await svgEl.boundingBox();
  if (box) {
    const scrollTo = Math.max(0, box.y + box.height - 850);
    await page.evaluate((y) => window.scrollTo(0, y), scrollTo);
    await page.waitForTimeout(500);
    console.log('STEP 6: scrolled to chart bottom, y offset:', scrollTo);
  }
}
await page.screenshot({ path: OUT('step6-chart-bottom') });

// Check for legend
const legendText = await page.evaluate(() => {
  const svgTexts = document.querySelectorAll('svg text');
  return Array.from(svgTexts).map(t => t.textContent).filter(t =>
    t && (t.includes('Improved') || t.includes('Worsened') || t.includes('Legend') ||
          t.includes('High') || t.includes('Low') || t.toLowerCase().includes('legend'))
  );
});
console.log('STEP 6: legend-related SVG texts:', JSON.stringify(legendText));

// STEP 7 — Scroll past chart
console.log('STEP 7: scrolling past chart to hero stats...');
const svgEl2 = await page.$('svg');
if (svgEl2) {
  const box = await svgEl2.boundingBox();
  if (box) {
    await page.evaluate((y) => window.scrollTo(0, y + 200), box.y + box.height);
  }
} else {
  await page.evaluate(() => window.scrollBy(0, 1200));
}
await page.waitForTimeout(500);
await page.screenshot({ path: OUT('step7-below-chart') });

const bodyText = await page.evaluate(() => document.body.innerText);
const hasHeroStats = bodyText.includes('%') && (bodyText.includes('countries') || bodyText.includes('Countries'));
const hasBreakdownBtn = bodyText.includes('breakdown') || bodyText.includes('Breakdown');
console.log('STEP 7: hero stats visible?', hasHeroStats, 'breakdown button?', hasBreakdownBtn);

// Find the breakdown button
const breakdownBtn = await page.$('button:has-text("breakdown"), button:has-text("Breakdown"), [class*="breakdown"], details, summary');
console.log('STEP 7: breakdown element:', !!breakdownBtn);
if (breakdownBtn) {
  const text = await breakdownBtn.innerText().catch(() => '');
  console.log('STEP 7: breakdown element text:', text.trim());
}

// STEP 8 — Click "Show detailed breakdown"
console.log('STEP 8: clicking breakdown button...');
if (breakdownBtn) {
  await breakdownBtn.click();
  await page.waitForTimeout(800);
  await page.screenshot({ path: OUT('step8-breakdown-open') });

  const afterText = await page.evaluate(() => document.body.innerText);
  const hasQuadrant = afterText.includes('quadrant') || afterText.includes('Quadrant') ||
                       afterText.includes('Improved') || afterText.includes('Worsened');
  const hasRegion = afterText.includes('Asia') || afterText.includes('Europe') ||
                     afterText.includes('Africa') || afterText.includes('Americas');
  console.log('STEP 8: quadrant content?', hasQuadrant, 'regional sections?', hasRegion);
} else {
  // Try clicking any element with breakdown text
  await page.evaluate(() => {
    const all = [...document.querySelectorAll('*')];
    const el = all.find(e => e.textContent.includes('detailed breakdown') || e.textContent.includes('Show breakdown'));
    if (el) el.click();
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: OUT('step8-breakdown-open') });
  console.log('STEP 8: tried clicking breakdown via text search');
}

// STEP 9 — Layout bug check: check for overlapping elements, z-index issues
console.log('STEP 9: checking for layout bugs...');
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForTimeout(300);
await page.screenshot({ path: OUT('step9-layout-check') });

const layoutIssues = await page.evaluate(() => {
  const issues = [];

  // Check for elements with overflow hidden cutting content
  const allEls = document.querySelectorAll('*');
  let truncated = 0;
  for (const el of allEls) {
    if (el.scrollHeight > el.clientHeight + 5 &&
        getComputedStyle(el).overflow === 'hidden' &&
        el.clientHeight > 10 && el.clientHeight < 500) {
      truncated++;
    }
  }
  if (truncated > 5) issues.push(`${truncated} elements have hidden overflow (possible text truncation)`);

  // Check for zero-size containers that should have content
  const containers = document.querySelectorAll('.chart-container, #chart-container, .chart-wrapper');
  for (const c of containers) {
    if (c.clientHeight === 0) issues.push(`Container ${c.className} has zero height`);
  }

  return issues;
});
console.log('STEP 9: layout issues:', JSON.stringify(layoutIssues));

await browser.close();
console.log('ALL STEPS COMPLETE');
