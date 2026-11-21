import { Extension, type Editor, type Range } from '@tiptap/core'
import Suggestion, { type SuggestionOptions } from '@tiptap/suggestion'
import { t } from '@/lib/i18n.ts'

export interface SlashItem {
  key: string
  label: string
  hint?: string
  run: (editor: Editor, range: Range) => void
}

export interface SlashCommandOptions {
  items: (query: string) => SlashItem[]
}

/** Go "/" o dau dong de mo menu chen block, giong slash command cua Notion. */
export const SlashCommand = Extension.create<SlashCommandOptions>({
  name: 'slashCommand',

  addOptions() {
    return { items: () => [] }
  },

  addProseMirrorPlugins() {
    const options: Omit<SuggestionOptions<SlashItem>, 'editor'> = {
      char: '/',
      allowSpaces: false,
      startOfLine: false,
      items: ({ query }) => this.options.items(query),
      command: ({ editor, range, props }) => {
        editor.chain().focus().deleteRange(range).run()
        props.run(editor, range)
      },
      render: () => {
        let root: HTMLDivElement | null = null
        let unmount: (() => void) | null = null
        let selected = 0
        let current: SlashItem[] = []
        let runCommand: ((item: SlashItem) => void) | null = null

        const renderList = (items: SlashItem[], command: (item: SlashItem) => void) => {
          if (!root) return
          current = items
          root.innerHTML = ''
          if (!items.length) {
            const empty = document.createElement('div')
            empty.className = 'slash-menu-empty'
            empty.textContent = t('Không có khối phù hợp')
            root.append(empty)
            return
          }
          items.forEach((item, i) => {
            const row = document.createElement('button')
            row.type = 'button'
            row.className = 'slash-menu-item' + (i === selected ? ' is-selected' : '')
            row.innerHTML = `<span class="slash-menu-label">${item.label}</span>` + (item.hint ? `<span class="slash-menu-hint">${item.hint}</span>` : '')
            row.addEventListener('mousedown', (e) => { e.preventDefault(); command(item) })
            root!.append(row)
          })
        }

        return {
          onStart: (props) => {
            selected = 0
            runCommand = props.command
            root = document.createElement('div')
            root.className = 'slash-menu'
            renderList(props.items, runCommand)
            unmount = props.mount?.(root) ?? null
            if (!unmount) document.body.append(root)
          },
          onUpdate: (props) => {
            selected = 0
            runCommand = props.command
            renderList(props.items, runCommand)
          },
          onKeyDown: (props) => {
            if (props.event.key === 'Escape') { unmount?.(); unmount = null; root?.remove(); return true }
            if (props.event.key === 'ArrowDown') { selected = (selected + 1) % Math.max(current.length, 1); renderList(current, runCommand!); return true }
            if (props.event.key === 'ArrowUp') { selected = (selected - 1 + Math.max(current.length, 1)) % Math.max(current.length, 1); renderList(current, runCommand!); return true }
            if (props.event.key === 'Enter') { const item = current[selected]; if (item) runCommand?.(item); return true }
            return false
          },
          onExit: () => { unmount?.(); unmount = null; root?.remove(); root = null },
        }
      },
    }
    return [Suggestion({ editor: this.editor, ...options })]
  },
})
