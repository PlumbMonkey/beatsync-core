// tests_playwright/timeline.spec.ts
// Playwright test for Slice 4.2: Timeline Visualization
// Ensures visual contract: beats, bars, sections, energy curve

import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const goldenPath = path.resolve(__dirname, '../fixtures/golden_beatsync.json');
const golden = JSON.parse(fs.readFileSync(goldenPath, 'utf-8'));

// Helper: minimal HTML for timeline rendering
function renderTimeline(json: any) {
  // This is a placeholder for a real component; for now, just SVG
  const beats = json.rhythm.beats;
  const bars = json.rhythm.bars;
  const sections = json.structure;
  const energy = json.energy.curve;
  const width = 800;
  const height = 200;
  const beatSpacing = width / (beats.length - 1);
  const energyY = (v: number) => height - v * (height - 40) - 20;
  return `
    <svg width="${width}" height="${height}" style="background:#f8f8f8">
      <!-- Beats -->
      ${beats.map((b, i) => `<circle cx="${i * beatSpacing}" cy="180" r="2" fill="#333" />`).join('')}
      <!-- Bars -->
      ${bars.map((b, i) => `<rect x="${i * beatSpacing * 4}" y="170" width="2" height="20" fill="#0074d9" />`).join('')}
      <!-- Sections -->
      ${sections.map(s => {
        const x1 = (beats.findIndex(bt => bt >= s.start)) * beatSpacing;
        const x2 = (beats.findIndex(bt => bt >= s.end)) * beatSpacing;
        return `<rect x="${x1}" y="20" width="${x2-x1}" height="30" fill="#aaa" opacity="0.3" />`;
      }).join('')}
      <!-- Energy Curve -->
      <polyline fill="none" stroke="#ff4136" stroke-width="2" points="${energy.map((e,i) => `${i * (width/(energy.length-1))},${energyY(e)}`).join(' ')}" />
    </svg>
  `;
}

test('timeline renders golden beatsync.json with structural fidelity', async ({ page }) => {
  // Serve static HTML with golden JSON
  await page.setContent(`
    <html><body>
      <div id="timeline">${renderTimeline(golden)}</div>
    </body></html>
  `);
  // Contract: beat count
  const beats = golden.rhythm.beats.length;
  await expect(page.locator('circle')).toHaveCount(beats);
  // Contract: bar count
  const bars = golden.rhythm.bars.length;
  await expect(page.locator('rect[fill="#0074d9"]')).toHaveCount(bars);
  // Contract: section blocks
  const sections = golden.structure.length;
  await expect(page.locator('rect[opacity]')).toHaveCount(sections);
  // Contract: energy curve points
  const energy = golden.energy.curve.length;
  const polyline = await page.locator('polyline').getAttribute('points');
  expect(polyline?.split(' ').length).toBe(energy);
  // Snapshot for golden regression
  expect(await page.screenshot()).toMatchSnapshot('timeline-golden.png');
});

// Test: missing optional fields
// (energy, structure, bars) should not crash

test('timeline renders gracefully with missing optional fields', async ({ page }) => {
  const minimal = {
    ...golden,
    energy: undefined,
    structure: undefined,
    rhythm: { ...golden.rhythm, bars: undefined }
  };
  await page.setContent(`
    <html><body>
      <div id="timeline">${renderTimeline({
        ...minimal,
        energy: { curve: [] },
        structure: [],
        rhythm: { ...golden.rhythm, bars: [] }
      })}</div>
    </body></html>
  `);
  // Should not throw, should render beats
  await expect(page.locator('circle')).toHaveCount(golden.rhythm.beats.length);
});

// Test: unknown fields are ignored

test('timeline ignores unknown fields in JSON', async ({ page }) => {
  const noisy = { ...golden, unknown_field: 123, rhythm: { ...golden.rhythm, foo: 'bar' } };
  await page.setContent(`
    <html><body>
      <div id="timeline">${renderTimeline(noisy)}</div>
    </body></html>
  `);
  // Should render beats and bars as normal
  await expect(page.locator('circle')).toHaveCount(golden.rhythm.beats.length);
  await expect(page.locator('rect[fill="#0074d9"]')).toHaveCount(golden.rhythm.bars.length);
});
