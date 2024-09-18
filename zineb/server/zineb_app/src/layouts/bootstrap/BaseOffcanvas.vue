<doc>
  - position: top, bottom, end, start
</doc>

<template>
  <div class="offcanvas-wrapper">
    <div :id="id" ref="link" :class="offcanvasClasses" tabindex="-1" aria-labelledby="offcanvasLabel">
      <div class="offcanvas-header">
        <h5 v-if="title" id="offcanvasLabel" class="offcanvas-title">
          {{ title }}
        </h5>
        <button type="button" class="btn-close text-reset" aria-label="Close" @click="$emit('close')"></button>
      </div>
  
      <div class="offcanvas-body">
        <slot></slot>
      </div>
  
      <slot name="footer"></slot>
    </div>

    <!-- Backdrop -->
    <div v-if="show && !allowScroll" :class="{ show }" class="offcanvas-backdrop fade" @click="handleStatic"></div>
  </div>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'BaseOffcanvas',
  props: {
    allowScroll: {
      type: Boolean
    },
    id: {
      type: String
    },
    position: {
      type: String,
      default: 'start'
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
    offcanvasClasses () {
      return [
        'offcanvas',
        {
          'text-bg-dark': this.darkMode,
          show: this.show
        },
        // this.darkMode ? 'bg-dark text-light' : 'bg-white text-dark',
        {
          [`offcanvas-${this.position}`]: true
        }
      ]
    }
  },
  watch: {
    show (current) {
      const body = document.body
      if (current) {
        if (!this.allowScroll) {
          body.style.overflow = 'hidden'
        }
        body.style.paddingRight = '17px'
        body.classList.add('offcanvas-open')

        this.$refs.link.style.visibility = 'visible'
      } else {
        body.style = null
        body.classList.remove('offcanvas-open')
        
        this.$refs.link.style.visibility = 'none'
      }
    }
  },
  methods: {
    handleStatic () {
      if (!this.staticBackdrop) {
        this.$emit('close')
      }
    }
  }
}
</script>
