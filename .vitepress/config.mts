import { defineConfig } from 'vitepress'
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const siteRoot = fileURLToPath(new URL('..', import.meta.url))
const contentDir = resolve(siteRoot, '系统设计笔记')

function firstHeading(file: string): string | null {
  const match = readFileSync(file, 'utf8').match(/^#\s+(.+)$/m)
  return match ? match[1].trim() : null
}

function slug(dirName: string): string {
  return dirName
    .replace(/^\d+\.\s*/, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

const rewrites: Record<string, string> = {
  'README.md': 'index.md',
}

const chapterSidebar: { text: string; link: string }[] = []

for (const entry of readdirSync(contentDir, { withFileTypes: true }).sort((a, b) =>
  a.name.localeCompare(b.name),
)) {
  if (!entry.isDirectory()) continue
  const readme = join(contentDir, entry.name, 'README.md')
  if (!existsSync(readme)) continue
  const num = entry.name.match(/^(\d+)\./)?.[1] ?? '00'
  const target = `${num}-${slug(entry.name)}/index.md`
  rewrites[`${entry.name}/README.md`] = target
  chapterSidebar.push({
    text: firstHeading(readme) ?? entry.name,
    link: `/${target.replace(/index\.md$/, '')}`,
  })
}

export default defineConfig({
  lang: 'zh-CN',
  title: '系统设计笔记',
  description: '《系统设计面试：内部指南》第一卷与第二卷中文笔记',
  srcDir: '系统设计笔记',
  cleanUrls: true,
  lastUpdated: false,
  rewrites,
  themeConfig: {
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一章', next: '下一章' },
    darkModeSwitchLabel: '主题',
    sidebarMenuLabel: '目录',
    returnToTopLabel: '回到顶部',
    lastUpdatedText: '更新于',
    search: { provider: 'local' },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/buxuele/system-design-notes' },
    ],
    sidebar: [{ text: '目录', link: '/' }, ...chapterSidebar],
  },
})
