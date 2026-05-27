import { cp, mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sourceRoot = path.join(root, 'docs');
const contentRoot = path.join(root, 'src', 'content', 'docs');
const generatedRoot = path.join(root, 'src', 'generated');
const publicGitBookRoot = path.join(root, 'public', '.gitbook');

const sourceToSlug = new Map();

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === '.gitbook') continue;
      files.push(...await walk(fullPath));
    } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.md') && entry.name !== 'SUMMARY.md') {
      files.push(fullPath);
    }
  }

  return files;
}

function toPosix(value) {
  return value.split(path.sep).join('/');
}

function outputRelativePath(sourcePath) {
  const relative = path.relative(sourceRoot, sourcePath);
  const parsed = path.parse(relative);
  if (parsed.base.toLowerCase() === 'readme.md') {
    return path.join(parsed.dir, 'index.md');
  }
  return relative;
}

function slugFromOutput(relativeOutputPath) {
  const noExt = relativeOutputPath.replace(/\.md$/i, '');
  return toPosix(noExt);
}

function cleanTitle(rawTitle, fallback) {
  const text = rawTitle
    .replace(/^#+\s*/, '')
    .replace(/<[^>]+>/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  return text || fallback;
}

function yamlString(value) {
  return JSON.stringify(value);
}

function stripFrontmatter(markdown) {
  if (!markdown.startsWith('---')) return { frontmatter: '', body: markdown };
  const end = markdown.indexOf('\n---', 3);
  if (end === -1) return { frontmatter: '', body: markdown };
  return {
    frontmatter: markdown.slice(3, end).trim(),
    body: markdown.slice(end + 4).replace(/^\r?\n/, ''),
  };
}

function descriptionFrom(frontmatter) {
  const single = frontmatter.match(/^description:\s*["']?(.+?)["']?\s*$/m);
  if (single) return single[1].trim();

  const folded = frontmatter.match(/^description:\s*>-\s*\r?\n((?:\s{2,}.+\r?\n?)+)/m);
  if (!folded) return '';

  return folded[1]
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .join(' ');
}

function normalizeGitBookMarkup(markdown) {
  return markdown
    .replace(/\{% embed url="([^"]+)" %\}/g, '[$1]($1)')
    .replace(/\{% file src="((?:\.\.\/)*\.gitbook\/assets\/([^"]+))" %\}/g, '[$2](/.gitbook/assets/$2)')
    .replace(/\{% content-ref url="([^"]+)" %\}/g, '')
    .replace(/\{% hint style="[^"]+" %\}/g, '')
    .replace(/\{% end(content-ref|hint) %\}/g, '')
    .replace(/\{% .*? %\}/g, '')
    .replace(/(<img\s+[^>]*src=")(?:\.\.\/)*\.gitbook\/assets\//g, '$1/.gitbook/assets/')
    .replace(/(!\[[^\]]*\]\()(?:\.\.\/)*\.gitbook\/assets\//g, '$1/.gitbook/assets/')
    .replace(/(!\[[^\]]*\]\(<)(?:\.\.\/)*\.gitbook\/assets\//g, '$1/.gitbook/assets/');
}

function rewriteMarkdownLinks(markdown, sourcePath) {
  return markdown.replace(/(\[[^\]]*\]\()([^)\s]+\.md)(#[^)]+)?(\))/g, (match, prefix, target, hash = '', suffix) => {
    if (/^(https?:)?\/\//i.test(target)) return match;

    const decodedTarget = decodeURI(target);
    const sourceDir = path.dirname(sourcePath);
    const targetSource = path.normalize(path.resolve(sourceDir, decodedTarget));
    const slug = sourceToSlug.get(targetSource.toLowerCase());
    if (!slug) return match;

    const relativeTarget = slug ? `/${slug}` : '/';
    return `${prefix}${relativeTarget}${hash}${suffix}`;
  });
}

function ensureFrontmatter(markdown, sourcePath) {
  const { frontmatter, body } = stripFrontmatter(markdown);
  const firstHeading = body.match(/^#\s+(.+)$/m);
  const fallback = path.basename(sourcePath, '.md').replace(/[-_]+/g, ' ');
  const title = cleanTitle(firstHeading?.[1] ?? '', fallback);
  const description = descriptionFrom(frontmatter);

  const generated = [
    '---',
    `title: ${yamlString(title)}`,
    description ? `description: ${yamlString(description)}` : '',
    '---',
    '',
  ].filter((line) => line !== '').join('\n');

  return `${generated}${body}`;
}

function parseSummary(summary) {
  const lines = summary.split(/\r?\n/);
  const sidebar = [];
  let currentGroup = null;

  for (const line of lines) {
    const heading = line.match(/^##\s+(.+)$/);
    if (heading) {
      currentGroup = {
        label: cleanTitle(heading[1], heading[1]),
        items: [],
      };
      sidebar.push(currentGroup);
      continue;
    }

    const item = line.match(/^(\s*)\*\s+\[([^\]]+)\]\(([^)]+)\)/);
    if (!item) continue;

    const indent = item[1].length;
    const label = cleanTitle(item[2], item[2]);
    const target = item[3];
    const resolved = path.normalize(path.resolve(sourceRoot, target));
    const slug = sourceToSlug.get(resolved.toLowerCase());
    if (slug === undefined) continue;

    const entry = { label, link: slug ? `/${slug}/` : '/' };
    if (!currentGroup && indent === 0) {
      if (slug === '' || slug === 'index') continue;
      sidebar.push(entry);
      continue;
    }

    if (!currentGroup) continue;

    if (indent <= 2) {
      currentGroup.items.push(entry);
    } else {
      const parent = currentGroup.items[currentGroup.items.length - 1];
      if (!parent) {
        currentGroup.items.push(entry);
      } else {
        parent.items ??= [];
        parent.items.push(entry);
      }
    }
  }

  return sidebar.map(normalizeSidebarItem);
}

function normalizeSidebarItem(item) {
  if (!item.items) return item;
  const { link, ...group } = item;
  group.items = group.items.map(normalizeSidebarItem);
  return group;
}

async function main() {
  const markdownFiles = await walk(sourceRoot);

  for (const file of markdownFiles) {
    const output = outputRelativePath(file);
    sourceToSlug.set(file.toLowerCase(), slugFromOutput(output));
  }

  await rm(contentRoot, { recursive: true, force: true });
  await rm(publicGitBookRoot, { recursive: true, force: true });
  await mkdir(contentRoot, { recursive: true });
  await mkdir(generatedRoot, { recursive: true });

  await cp(path.join(sourceRoot, '.gitbook'), publicGitBookRoot, { recursive: true });

  for (const file of markdownFiles) {
    const relativeOutput = outputRelativePath(file);
    const output = path.join(contentRoot, relativeOutput);
    const source = await readFile(file, 'utf8');
    const normalized = rewriteMarkdownLinks(
      normalizeGitBookMarkup(ensureFrontmatter(source, file)),
      file,
    );

    await mkdir(path.dirname(output), { recursive: true });
    await writeFile(output, normalized, 'utf8');
  }

  const summary = await readFile(path.join(sourceRoot, 'SUMMARY.md'), 'utf8');
  const sidebar = parseSummary(summary);
  await writeFile(
    path.join(generatedRoot, 'sidebar.mjs'),
    `export default ${JSON.stringify(sidebar, null, 2)};\n`,
    'utf8',
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
