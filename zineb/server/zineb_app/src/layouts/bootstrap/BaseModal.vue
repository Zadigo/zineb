<template>
  <div ref="link" class="modal-wrapper">
    <transition :name="currentAnimation">
      <div v-if="show" :id="id" :class="modalClasses" :aria-modal="show" class="modal" role="dialog" tabindex="-1">
        <div :class="modalDialogClasses" class="modal-dialog">
          <div :class="modalContentClasses" class="modal-content">
            <div v-if="!isFrame" class="modal-header">
              <h5 v-if="title" class="modal-title">
                {{ title }}
              </h5>
              <button type="button" class="btn-close" aria-label="Close" @click="$emit('close')"></button>
            </div>
  
            <div class="modal-body">
              <slot></slot>
            </div>
  
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </transition>
    
    <transition name="modal-backdrop">
      <div v-if="show && !nonInvasive" :class="{ show }" class="modal-backdrop"></div>
    </transition>
  </div>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'BaseModal',
  props: {
    id: {
      type: String,
      required: true
    },
    centered: {
      type: Boolean
    },
    nonInvasive: {
      type: Boolean
    },
    position: {
      type: String,
      default: null
    },
    scrollable: {
      type: Boolean
    },
    size: {
      type: String,
      default: 'lg'
    },
    show: {
      type: Boolean
    },
    staticBackdrop: {
      type: Boolean
    },
    title: {
      type: String
    }
  },
  emits: {
    close () {
      return true
    }
  },
  setup () {
    const darkMode = inject('darkMode', false)
    return {
      darkMode
    }
  },
  computed: {
    modalClasses () {
      let position = this.position
      switch (this.position) {
        case 'top-left':
        case 'bottom-left':
          position = 'left'
          break

        case 'top-right':
        case 'bottom-right':
          position = 'right'
          break
      
        default:
          break
      }
      return [
        {
          show: this.show
        },
        position
      ]
    },
    modalDialogClasses () {
      if (this.hasPositionX) {
        return [
          {
            [`modal-side modal-${this.position}`]: true
          }
        ]
      }

      if (this.hasPositionY) {
        return [
          {
            [`modal-frame modal-${this.position}`]: true
          }
        ]
      }

      return [
        {
          [`modal-${this.size}`]: true,
          'modal-dialog-centered': this.centered,
          'modal-dialog-scrollable': this.scrollable
        }
      ]
    },
    modalContentClasses () {
      return [
        this.hasPositionY ? 'rounded-0' : null,
        this.darkMode ? 'bg-dark text-light' : 'bg-white text-dark'
      ]  
    },
    currentAnimation () {
      if (this.position === 'fullscreen') {
        return 'modal-from-bottom'
      }

      if (this.position === 'top-left' || this.position === 'bottom-left') {
        return 'modal-from-left'
      }

      if (this.position === 'top-right' || this.position === 'bottom-right') {
        return 'modal-from-right'
      }

      if (this.position === 'bottom') {
        return 'modal-from-bottom'
      }

      return 'modal-from-top'
    },
    hasPositionX () {
      const positions = ['right', 'left', 'top-right', 'top-left', 'bottom-left', 'bottom-right']
      return this.position && positions.includes(this.position)
    },
    hasPositionY () {
      return this.position && this.position === 'top' || this.position === 'bottom'
    },
    isFrame () {
      return ['top', 'bottom'].includes(this.position)
    }
  },
  watch: {
    show (current) {
      this.toggleHtmlBody()

      if (current) {
        this.$refs.link.scrollTop
      } else {
        this.reflow()
      }
    }
  },
  mounted () {
    const body = this.getBody()
    body.addEventListener('click', this.backdropClick)
  },
  beforeUnmount () {
    const body = this.getBody()
    body.removeEventListener('click', this.backdropClick)
  },
  methods: {
    toggleHtmlBody () {
      const body = this.getBody()

      if (body.classList.contains('modal-open')) {
        body.classList.remove('modal-open')
        // body.style.overflow = null
      } else {
        body.classList.add('modal-open')
        // body.style.overflow = 'hidden'
      }
    },
    getBody () {
      return document.querySelector('body')
    },
    backdropClick (e) {
      if (e.target.classList.contains('modal')) {
        if (this.staticBackdrop) {
          e.target.classList.add('modal-static')

          setTimeout(() => {
            e.target.classList.remove('modal-static')
          }, 300)
        } else {
          this.$emit('close')
        }
      }
    },
    reflow () {
      this.$refs.link.offsetHeight
    }
  }
}
</script>

<style scoped>
.modal.show {
  display: block;
  overflow-y: auto;
}

.modal-backdrop.show {
  opacity: .5;
}
</style>
