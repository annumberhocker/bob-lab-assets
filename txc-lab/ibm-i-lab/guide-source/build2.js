const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, AlignmentType, LevelFormat, PageBreak, ExternalHyperlink } = require('docx');

const SRC = process.argv[2], OUT = process.argv[3];
const AUDIENCE = (process.argv[4] || 'all').toLowerCase();   // participant | facilitator | all
const md = fs.readFileSync(SRC, 'utf8').split('\n');
const FONT = 'Calibri', CODE = 'Consolas';
const PAGE_W = 12240, MARGIN = 1080, CONTENT_W = PAGE_W - 2 * MARGIN;
const NAVY = '1F3864', BLUE = '2F5496';

function runs(text, base = {}) {
  text = text.replace(/\\\*/g, '*');
  const out = []; const re = /(\*\*[^*]+\*\*|`[^`]+`|https?:\/\/[^\s)]+)/g; let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, ...base }));
    const t = m[0];
    if (t.startsWith('**')) out.push(new TextRun({ text: t.slice(2, -2), bold: true, font: FONT, ...base }));
    else if (t.startsWith('http')) out.push(new ExternalHyperlink({ link: t, children: [new TextRun({ text: t, font: FONT, style: 'Hyperlink', ...base })] }));
    else out.push(new TextRun({ text: t.slice(1, -1), font: CODE, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, ...base }));
  return out;
}

const thin = { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF' };
const borders = { top: thin, bottom: thin, left: thin, right: thin };

function cell(text, width, opts) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders,
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill } : undefined,
    margins: { top: 70, bottom: 70, left: 110, right: 110 },
    children: [new Paragraph({ children: runs(text, { size: 19, bold: !!opts.bold }), spacing: { before: 0, after: 0 } })],
  });
}

function makeTable(rows, kv) {
  const ncol = rows[0].length;
  const lens = rows[0].map((_, i) => Math.max(...rows.map(r => (r[i] || '').length)));
  const weights = lens.map((l, i) => Math.min(Math.max(l, rows[0][i].length + 3, 15), 60));
  if (kv) { weights[0] = 14; weights[1] = 60; }
  const total = weights.reduce((a, b) => a + b, 0);
  const widths = weights.map(w => Math.round(CONTENT_W * w / total));
  widths[ncol - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({
      tableHeader: !kv && ri === 0, cantSplit: true,
      children: r.map((c, ci) => cell(c, widths[ci], kv ? { bold: ci === 0, fill: ci === 0 ? 'F2F2F2' : null } : { bold: ri === 0, fill: ri === 0 ? 'D9E2F3' : null })),
    })),
  });
}

function caption(text) {
  return new Paragraph({ children: [new TextRun({ text, italics: true, size: 16, color: '595959', font: FONT })], spacing: { before: 40, after: 0, line: 200 }, keepNext: true });
}
function box(text, fill, leftColor, mono) {
  const b = { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF', space: 4 };
  const l = { style: BorderStyle.SINGLE, size: 24, color: leftColor, space: 4 };
  const isUrl = /^https?:\/\/\S+$/.test(text.trim());
  const kids = isUrl
    ? [new ExternalHyperlink({ link: text.trim(), children: [new TextRun({ text: text.trim(), font: CODE, size: 19, style: 'Hyperlink' })] })]
    : runs(text, mono ? { font: CODE, size: 19 } : { size: 20 });
  return new Paragraph({
    children: kids,
    shading: { type: ShadingType.CLEAR, fill },
    border: { top: b, bottom: b, right: b, left: l },
    indent: { left: 120, right: 120 },
    spacing: { before: 20, after: 100 },
    keepLines: true,
  });
}

const children = [];
let i = 0, listId = 0, inNumbered = false, kvNext = false, breakNext = false, region = null;
while (i < md.length) {
  const line = md[i];
  // audience regions: %par ... %end and %fac ... %end; auto-tag facilitator callouts
  // the facilitator edition is the setup document: it ends where the exercises begin
  if (AUDIENCE === 'facilitator' && line.startsWith('## Key concept: modes')) break;
  if (line.trim() === '%par') { region = 'participant'; i++; continue; }
  if (line.trim() === '%fac') { region = 'facilitator'; i++; continue; }
  if (line.trim() === '%end') { region = null; i++; continue; }
  if (region && AUDIENCE !== 'all' && region !== AUDIENCE) { i++; continue; }
  if (AUDIENCE === 'participant' && line.startsWith('!! **FACILITATOR')) { i++; continue; }
  if (!line.trim()) { i++; continue; }
  if (!/^\d+\. /.test(line)) inNumbered = false;
  if (line.startsWith('#sub ')) { children.push(new Paragraph({ children: runs(line.slice(5), { size: 28, color: BLUE }), spacing: { after: 360 } })); i++; continue; }
  if (line.startsWith('# ')) { children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: runs(line.slice(2)) })); i++; continue; }
  if (line.startsWith('## ')) { children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: breakNext, children: runs(line.slice(3)), spacing: { before: 120, after: 160 } })); breakNext = false; i++; continue; }
  if (line.startsWith('### ')) { children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(line.slice(4)), spacing: { before: 240, after: 100 }, keepNext: true })); i++; continue; }
  if (line.trim() === '---') { breakNext = true; i++; continue; }
  if (line.trim() === '%kv') { kvNext = true; i++; continue; }
  if (line.startsWith('|')) {
    const rows = [];
    while (i < md.length && md[i].startsWith('|')) {
      const cells = md[i].trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(s => s.trim());
      if (!cells.every(c => /^-+$/.test(c))) rows.push(cells);
      i++;
    }
    children.push(makeTable(rows, kvNext)); kvNext = false;
    // no spacer when a page break follows: a lone spacer at a page end would make a blank page
    let k = i; while (k < md.length && (!md[k].trim() || /^%(par|fac|end)$/.test(md[k].trim()))) k++;
    if (!(k < md.length && md[k].trim() === '---')) children.push(new Paragraph({ children: [], spacing: { after: 100 } }));
    continue;
  }
  if (line.startsWith('!! ')) { children.push(box(line.slice(3), 'FFF8E1', 'E0A800', false)); i++; continue; }
  if (line.startsWith('$$ ')) { children.push(caption(/^https?:\/\//.test(line.slice(3).trim()) ? 'Open in a browser' : 'Type in the terminal')); children.push(box(line.slice(3), 'F2F2F2', '595959', true)); i++; continue; }
  if (line.startsWith('>> ')) { children.push(caption('Paste into the Bob chat')); children.push(box(line.slice(3), 'EEF3FA', '2F5496', true)); i++; continue; }
  if (line.startsWith('== ')) { children.push(caption('What you should see')); children.push(box(line.slice(3), 'F7F7F7', 'A6A6A6', true)); i++; continue; }
  if (line.startsWith('✓ ')) { children.push(box('✓ ' + line.slice(2), 'E8F5E9', '2E7D32', false)); i++; continue; }
  if (line.startsWith('?? ')) { children.push(new Paragraph({ children: runs(line.slice(3), { italics: true, color: '404040' }), indent: { left: 360 }, spacing: { after: 120 } })); i++; continue; }
  if (/^- /.test(line)) { children.push(new Paragraph({ numbering: { reference: 'bullets', level: 0 }, children: runs(line.slice(2)), spacing: { after: 60 } })); i++; continue; }
  if (/^\d+\. /.test(line)) {
    if (!inNumbered && (/^1\. /.test(line) || listId === 0)) { listId++; }
    inNumbered = true;
    children.push(new Paragraph({ numbering: { reference: 'numbers' + listId, level: 0 }, children: runs(line.replace(/^\d+\. /, '')), spacing: { after: 50 } }));
    i++; continue;
  }
  let text = line; i++;
  while (i < md.length && md[i].trim() && !/^(#|\||- |\d+\. |---|!! |\$\$ |>> |== |✓ |\?\? |%kv|%par|%fac|%end)/.test(md[i])) { text += ' ' + md[i].trim(); i++; }
  children.push(new Paragraph({ children: runs(text), spacing: { after: 100 } }));
}

const lvl = (fmt, txt) => [{ level: 0, format: fmt, text: txt, alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }];
const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 21 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', run: { size: 44, bold: true, color: NAVY, font: FONT }, paragraph: { spacing: { after: 60 } } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 32, bold: true, color: NAVY, font: FONT }, paragraph: { outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 24, bold: true, color: BLUE, font: FONT }, paragraph: { outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: 'bullets', levels: lvl(LevelFormat.BULLET, '•') },
    ...Array.from({ length: listId }, (_, k) => ({ reference: 'numbers' + (k + 1), levels: lvl(LevelFormat.DECIMAL, '%1.') })),
  ] },
  sections: [{ properties: { page: { size: { width: PAGE_W, height: 15840 }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } }, children }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log('wrote'); });
