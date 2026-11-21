import { mergeAttributes, Node } from '@tiptap/core'

export interface PageLinkOptions {
  onOpen: (pageId: string) => void
  resolveTitle: (pageId: string) => string | undefined
}

/** Block "chip" tro den mot trang con, giong sub-page block trong Notion. Tieu de luon lay runtime tu danh sach trang. */
export const PageLink = Node.create<PageLinkOptions>({
  name: 'pageLink',
  group: 'block',
  atom: true,
  selectable: true,
  draggable: true,

  addOptions() {
    return { onOpen: () => undefined, resolveTitle: () => undefined }
  },

  addAttributes() {
    return {
      pageId: { default: '' },
      title: { default: '' },
    }
  },

  parseHTML() {
    return [{ tag: 'div[data-type="page-link"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'page-link' })]
  },

  addNodeView() {
    return ({ node }) => {
      const dom = document.createElement('div')
      dom.dataset.type = 'page-link'
      dom.contentEditable = 'false'
      dom.tabIndex = 0
      const apply = () => {
        const title = this.options.resolveTitle(node.attrs.pageId) ?? node.attrs.title ?? ''
        dom.textContent = `📄 ${title}`
      }
      apply()
      dom.addEventListener('click', (e) => { e.preventDefault(); this.options.onOpen(node.attrs.pageId) })
      return {
        dom,
        update: (updated) => {
          if (updated.type.name !== 'pageLink') return false
          node = updated
          apply()
          return true
        },
      }
    }
  },
})
