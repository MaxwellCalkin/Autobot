#!/usr/bin/env node
/**
 * Autobot Observation Analyzer - Mine patterns from observations.jsonl.
 *
 * Utility script for querying and analyzing observations logged during
 * autonomous development sessions.
 *
 * Usage:
 *   node analyze-observations.js --type test_failure
 *   node analyze-observations.js --recent 10
 *   node analyze-observations.js --summary
 */
import fs from 'fs';

function loadObservations(filePath) {
  const observations = [];
  if (!fs.existsSync(filePath)) return observations;

  const content = fs.readFileSync(filePath, 'utf-8');
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try {
      observations.push(JSON.parse(trimmed));
    } catch {
      // Skip invalid lines
    }
  }
  return observations;
}

function filterByType(observations, type) {
  return observations.filter(o => o.type === type);
}

function getRecent(observations, count) {
  return observations.slice(-count);
}

function printSummary(observations) {
  if (observations.length === 0) {
    console.log('No observations found.');
    return;
  }

  const typeCounts = {};
  const fileCounts = {};

  for (const obs of observations) {
    const type = obs.type || 'unknown';
    typeCounts[type] = (typeCounts[type] || 0) + 1;
    if (obs.file) {
      fileCounts[obs.file] = (fileCounts[obs.file] || 0) + 1;
    }
  }

  console.log('=== OBSERVATION SUMMARY ===\n');
  console.log(`Total observations: ${observations.length}`);

  console.log('\nBy Type:');
  const sortedTypes = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]);
  for (const [type, count] of sortedTypes) {
    console.log(`  ${type}: ${count}`);
  }

  console.log('\nMost Affected Files:');
  const sortedFiles = Object.entries(fileCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
  for (const [file, count] of sortedFiles) {
    console.log(`  ${file}: ${count}`);
  }

  const timestamps = observations.map(o => o.timestamp).filter(Boolean);
  if (timestamps.length > 0) {
    timestamps.sort();
    console.log('\nTime Range:');
    console.log(`  First: ${timestamps[0]}`);
    console.log(`  Last: ${timestamps[timestamps.length - 1]}`);
  }
}

function printObservations(observations) {
  for (let i = 0; i < observations.length; i++) {
    const obs = observations[i];
    console.log(`\n--- Observation ${i + 1} ---`);
    console.log(`Type: ${obs.type || 'unknown'}`);
    console.log(`Time: ${obs.timestamp || 'unknown'}`);
    if (obs.file) console.log(`File: ${obs.file}`);
    if (obs.message) console.log(`Message: ${obs.message}`);
    if (obs.output_snippet) console.log(`Output: ${obs.output_snippet.slice(0, 200)}...`);
  }
}

function main() {
  const args = process.argv.slice(2);
  let type = null;
  let recent = null;
  let summary = false;
  let obsPath = '.autobot/observations.jsonl';

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--type' && args[i + 1]) {
      type = args[++i];
    } else if (args[i] === '--recent' && args[i + 1]) {
      recent = parseInt(args[++i], 10);
    } else if (args[i] === '--summary') {
      summary = true;
    } else if (args[i] === '--path' && args[i + 1]) {
      obsPath = args[++i];
    }
  }

  let observations = loadObservations(obsPath);

  if (type) {
    observations = filterByType(observations, type);
    console.log(`Filtered to ${observations.length} observations of type '${type}'`);
  }

  if (recent) {
    observations = getRecent(observations, recent);
  }

  if (summary) {
    printSummary(observations);
  } else {
    printObservations(observations);
  }
}

main();
