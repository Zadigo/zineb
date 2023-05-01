<template>
  <div ref="link" class="card-reveal">
    <transition name="slide" mode="out-in">
      <div v-if="reveal" class="reveal">
        <div class="row">
          <div class="col-12 mb-2">
            <button type="button" class="btn-close" @click="reveal = false"></button>
          </div>

          <div class="col-12">
            {{ content }}
          </div>
        </div>
      </div>
      <button v-else type="button" class="btn-reveal btn btn-primary btn-floating" @click="reveal = true">
        <font-awesome-icon icon="fa-solid fa-plus" />
      </button>
    </transition>
  </div>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'BaseCardReveal',
  props: {
    content: {
      type: String
    }
  },
  setup (props, { slots }) {
    const darkMode = inject('darkMode', false)
    const parent = null
    const cardHeight = 0
    const hasReveal = !!slots.reveal
    return {
      parent,
      cardHeight,
      darkMode,
      hasReveal
    }
  },
  data () {
    return {
      reveal: false
    }
  },
  computed: {
    
  },
  // mounted () {
  //   this.parent = this.$refs.link.parentElement
  //   this.cardHeight = this.parent.offsetHeight
  //   const button = this.$refs.link.querySelector('.btn-reveal')
  //   button.style.positionTop = `${this.cardHeight / 2}px`
  // }
}
</script>

<style scoped>
.card-reveal .reveal {
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
  background-color: white;
  height: 100%;
  width: 100%;
  border-radius: .5rem;
  padding: .5rem;
}

.card-reveal .btn-reveal {
  position: absolute;
  top: 50%;
  right: 5%;
}
</style>
