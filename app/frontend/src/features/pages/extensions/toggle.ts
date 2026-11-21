import { mergeAttributes, Node } from '@tiptap/core'
import { t } from '@/lib/i18n.ts'

/** Block gap/mo kieu Notion: dong dau (paragraph) la tieu de luon hien, cac block sau la noi dung an/hien theo attrs.open.
 * Bam vao mui ten truoc dong dau de dong/mo; go chu binh thuong trong dong dau va trong noi dung. */
export const Toggle = Node.create({
  name: 'toggle',
  group: 'block',
  content: 'paragraph block*',
  defining: true,

  addAttributes() {
    return {
      open: { default: false, parseHTML: (el) => el.getAttribute('data-open') === 'true', renderHTML: (attrs) => ({ 'data-open': attrs.open ? 'true' : 'false' }) },
    }
  },

  parseHTML() {
    return [{ tag: 'div[data-type="toggle"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'toggle' }), 0]
  },

  addNodeView() {
    return ({ node, getPos, editor }) => {
      const wrapper = document.createElement('div')
      wrapper.dataset.type = 'toggle'
      const caret = document.createElement('button')
      caret.type = 'button'
      caret.contentEditable = 'false'
      caret.dataset.toggleCaret = ''
      caret.setAttribute('aria-label', t('Thu gọn/mở rộng'))
      caret.addEventListener('mousedown', (e) => e.preventDefault())
      caret.addEventListener('click', () => {
        if (typeof getPos !== 'function') return
        const pos = getPos()
        if (pos == null) return
        editor.chain().command(({ tr }) => {
          tr.setNodeAttribute(pos, 'open', !wrapper.dataset.open || wrapper.dataset.open === 'false')
          return true
        }).run()
      })
      wrapper.append(caret)
      const content = document.createElement('div')
      content.dataset.toggleContent = ''
      wrapper.append(content)
      const apply = (open: boolean) => { wrapper.dataset.open = open ? 'true' : 'false' }
      apply(!!node.attrs.open)
      return {
        dom: wrapper,
        contentDOM: content,
        update: (updated) => {
          if (updated.type.name !== 'toggle') return false
          apply(!!updated.attrs.open)
          return true
        },
      }
    }
  },
})
