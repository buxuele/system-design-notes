import { createMarkdownRenderer } from 'vitepress'
import { parse } from '@vue/compiler-dom'
import { readdirSync, readFileSync } from 'node:fs'
import { join, resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const contentDir = join(root, '系统设计笔记')
const md = await createMarkdownRenderer(root)

function collect(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = join(dir, entry.name)
    if (entry.isDirectory()) return collect(full)
    return entry.name.endsWith('.md') ? [full] : []
  })
}

let failed = 0
const files = collect(contentDir)
for (const file of files) {
  const html = md.render(readFileSync(file, 'utf8'))
  try {
    parse(html)
  } catch (error) {
    failed += 1
    const line = error.loc?.start?.line
    const snippet = line ? html.split('\n')[line - 1] : ''
    console.error(`${file.slice(root.length + 1)}: ${error.message} @${line} ${snippet}`)
  }
}
console.log(`checked=${files.length} failed=${failed}`)
process.exit(failed ? 1 : 0)
