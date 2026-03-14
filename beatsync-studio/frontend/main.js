// main.js — minimal loader for timeline
import { renderTimeline } from './timeline.js';

fetch('./fixtures/golden_beatsync.json')
  .then(r => r.json())
  .then(json => {
    document.getElementById('timeline').innerHTML = renderTimeline(json);
  });
