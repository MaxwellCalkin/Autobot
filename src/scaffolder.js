import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');

export function checkExistingState(projectDir) {
  const claudeDir = path.join(projectDir, '.claude');
  const autobotDir = path.join(projectDir, '.autobot');

  const claudeExists = fs.existsSync(claudeDir);
  const autobotExists = fs.existsSync(autobotDir);

  let activeTask = null;
  if (autobotExists) {
    const taskFile = path.join(autobotDir, 'task.json');
    if (fs.existsSync(taskFile)) {
      try {
        const task = JSON.parse(fs.readFileSync(taskFile, 'utf-8'));
        if (task.status === 'in_progress' || task.status === 'paused') {
          activeTask = task;
        }
      } catch {
        // Invalid JSON - ignore
      }
    }
  }

  return { claudeExists, autobotExists, activeTask };
}

export function scaffoldProject(projectDir, { force = false, resetAutobot = false } = {}) {
  const createdFiles = [];

  // Scaffold .claude/ directory
  const claudeSource = path.join(TEMPLATES_DIR, 'claude');
  const claudeDest = path.join(projectDir, '.claude');
  createdFiles.push(...copyTemplateTree(claudeSource, claudeDest, projectDir, force));

  // Scaffold .autobot/ directory
  const autobotSource = path.join(TEMPLATES_DIR, 'autobot');
  const autobotDest = path.join(projectDir, '.autobot');
  createdFiles.push(...copyTemplateTree(autobotSource, autobotDest, projectDir, force || resetAutobot));

  // Copy CLAUDE.md to project root
  const claudeMdSource = path.join(TEMPLATES_DIR, 'CLAUDE.md');
  const claudeMdDest = path.join(projectDir, 'CLAUDE.md');
  if (copyTemplateFile(claudeMdSource, claudeMdDest, force)) {
    createdFiles.push('CLAUDE.md');
  }

  return createdFiles;
}

function copyTemplateTree(source, dest, projectDir, force) {
  const createdFiles = [];
  fs.mkdirSync(dest, { recursive: true });

  const entries = fs.readdirSync(source, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(source, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      createdFiles.push(...copyTemplateTree(srcPath, destPath, projectDir, force));
    } else {
      if (copyTemplateFile(srcPath, destPath, force)) {
        createdFiles.push(path.relative(projectDir, destPath));
      }
    }
  }

  return createdFiles;
}

function copyTemplateFile(source, dest, force) {
  if (fs.existsSync(dest) && !force) {
    return false;
  }

  fs.mkdirSync(path.dirname(dest), { recursive: true });

  try {
    const content = fs.readFileSync(source, 'utf-8');
    fs.writeFileSync(dest, content, 'utf-8');
  } catch {
    // Binary file fallback
    const content = fs.readFileSync(source);
    fs.writeFileSync(dest, content);
  }

  return true;
}
