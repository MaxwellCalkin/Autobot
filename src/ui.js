import chalk from 'chalk';
import { createInterface } from 'readline';

const IS_WINDOWS = process.platform === 'win32';

export const CHECK = IS_WINDOWS ? chalk.green('OK') : chalk.green('\u2713');
export const CROSS = IS_WINDOWS ? chalk.red('X') : chalk.red('\u2717');

export function printPanel(lines, { borderColor = 'blue' } = {}) {
  const colorFn = chalk[borderColor] || chalk.blue;
  const content = Array.isArray(lines) ? lines : [lines];
  const maxLen = Math.max(...content.map(l => stripAnsi(l).length));
  const border = colorFn('\u2500'.repeat(maxLen + 2));

  console.log();
  console.log(colorFn('\u250c') + border + colorFn('\u2510'));
  for (const line of content) {
    const pad = ' '.repeat(maxLen - stripAnsi(line).length);
    console.log(colorFn('\u2502') + ' ' + line + pad + ' ' + colorFn('\u2502'));
  }
  console.log(colorFn('\u2514') + border + colorFn('\u2518'));
  console.log();
}

function stripAnsi(str) {
  return str.replace(/\x1b\[[0-9;]*m/g, '');
}

export function confirm(message) {
  return new Promise((resolve) => {
    const rl = createInterface({ input: process.stdin, output: process.stdout });
    rl.question(`${message} [y/N] `, (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === 'y');
    });
  });
}
