import { mergeAttributes, Node } from '@tiptap/core'
import { t } from '@/lib/i18n.ts'

export const CALLOUT_COLORS = ['gray', 'blue', 'green', 'yellow', 'red', 'purple'] as const
export type CalloutColor = typeof CALLOUT_COLORS[number]

/** Khoi highlight co icon + mau nen, giong callout trong Notion. */
export const Callout = Node.create<{ editIcon: (current: string) => Promise<string | null> }>({
  name: 'callout',
  group: 'block',
  content: 'block+',
  defining: true,

  addOptions() {
    return { editIcon: async () => null }
  },

  addAttributes() {
    return {
      icon: { default: '💡', parseHTML: (el) => el.getAttribute('data-icon') ?? '💡', renderHTML: (attrs) => ({ 'data-icon': attrs.icon }) },
      color: { default: 'gray', parseHTML: (el) => el.getAttribute('data-color') ?? 'gray', renderHTML: (attrs) => ({ 'data-color': attrs.color }) },
    }
  },

  parseHTML() {
    return [{ tag: 'div[data-type="callout"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'callout' }), 0]
  },

  addNodeView() {
    return ({ node, getPos, editor }) => {
      const wrapper = document.createElement('div')
      wrapper.dataset.type = 'callout'
      const iconEl = document.createElement('button')
      iconEl.type = 'button'
      iconEl.contentEditable = 'false'
      iconEl.dataset.calloutIcon = ''
      iconEl.setAttribute('aria-label', t('Đổi biểu tượng'))
      iconEl.addEventListener('mousedown', (e) => e.preventDefault())
      iconEl.addEventListener('click', async () => {
        const next = await this.options.editIcon(iconEl.textContent || '💡')
        if (next == null || editor.isDestroyed || !wrapper.isConnected || typeof getPos !== 'function') return
        const pos = getPos()
        if (pos == null) return
        editor.chain().focus().command(({ tr }) => { tr.setNodeAttribute(pos, 'icon', next.slice(0, 8) || '💡'); return true }).run()
      })
      wrapper.append(iconEl)
      const content = document.createElement('div')
      content.dataset.calloutContent = ''
      wrapper.append(content)
      const swatches = document.createElement('div')
      swatches.dataset.calloutSwatches = ''
      swatches.contentEditable = 'false'
      for (const color of CALLOUT_COLORS) {
        const dot = document.createElement('button')
        dot.type = 'button'
        dot.dataset.swatch = color
        dot.setAttribute('aria-label', color)
        dot.addEventListener('mousedown', (e) => e.preventDefault())
        dot.addEventListener('click', () => {
          if (typeof getPos !== 'function') return
          const pos = getPos()
          if (pos == null) return
          editor.chain().focus().command(({ tr }) => { tr.setNodeAttribute(pos, 'color', color); return true }).run()
        })
        swatches.append(dot)
      }
      wrapper.append(swatches)
      const apply = (icon: string, color: string) => { iconEl.textContent = icon; wrapper.dataset.color = color }
      apply(node.attrs.icon, node.attrs.color)
      return {
        dom: wrapper,
        contentDOM: content,
        update: (updated) => {
          if (updated.type.name !== 'callout') return false
          apply(updated.attrs.icon, updated.attrs.color)
          return true
        },
      }
    }
  },
})
