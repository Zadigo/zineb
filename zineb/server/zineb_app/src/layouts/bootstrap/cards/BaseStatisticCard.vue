<template>
  <div ref="link" :class="cardClasses" class="card">
    <!-- Header -->
    <div v-if="hasHeader" class="card-header">
      <slot name="header"></slot>
    </div>

    <div class="stats">
      <div class="one-third">
        <div class="stat">$20</div>
        <div class="stat-value">Training</div>
      </div>
    
      <div class="one-third">
        <div class="stat">16</div>
        <div class="stat-value">Speed</div>
      </div>
    
      <div class="one-third">
        <div class="stat">$150</div>
        <div class="stat-value">Cost</div>
      </div>
    </div>
  </div>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'BaseCard',
  props: {
    hoverable: {
      type: Boolean
    }
  },
  setup (props, { slots }) {
    const darkMode = inject('darkMode', false)
    const cardHeight = null

    const hasHeader = !!slots.header
    const hasFooter = !!slots.footer
    const hasReveal = !!slots.reveal
    return {
      darkMode,
      hasHeader,
      hasFooter,
      hasReveal,
      cardHeight
    }
  },
  data () {
    return {
      reveal: false
    }
  },
  computed: {
    cardClasses () {
      return [
        {
          'bg-dark': this.darkMode,
          'hoverable': this.hoverable
        }
      ]
    }
  },
  mounted () {
    this.cardHeight = this.$refs.link.offsetHeight
  }
}
</script>

<style scoped>
.card {
  position: relative;
}

.text-bg-dark {
  color: #fff !important;
  background-color: rgba(33, 37, 41, 1, 1) !important;
}

.stats {
  /* background: #ec9b3b; */
  background: rgba(0, 0, 0, 0.03);
  /* color: white; */
  /* color: rgba(38, 38, 38, 1); */
  color: #212529;
  font-weight: 700;
  border-bottom-left-radius: .5rem;
  border-bottom-right-radius: .5rem;
  /* border-top: 1px solid rgba(0, 0, 0, 0.175); */
  text-align: center;
}

.stats .one-third {
  width: 33%;
  float: left;
  padding: 20px 15px;
}

.stats .stat {
  position: relative;
  font-size: 24px;
}

.stats .stat-value {
  text-transform: uppercase;
  font-weight: 400;
  font-size: 12px;
}

.stats .one-third:not(:last-child) {
  /* border-right: 1px solid #bd7c2f; */
  border-right: 1px solid rgba(0, 0, 0, 0.175);
}

.card .halfway-fab {
  position: absolute;
  right: 24px;
  bottom: calc((546px / 2 + 18px));
  z-index: 4;
}

.waves-effect {
  position: relative;
  cursor: pointer;
  display: inline-block;
  overflow: hidden;
  user-select: none;
  vertical-align: middle;
  z-index: 1;
  transition: .3s ease-out;
}

/* .card-reveal {
  overflow: hidden;
}
.reveal {
  position: absolute;
  background-color: #fff;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  border-radius: calc(.5rem - 1px);
  z-index: 5;
  padding: 1rem;
} */
.slide-enter-active,
.slide-leave-active {
  transition: all .3s ease-in-out;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(100%);
}

.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  transform: translateY(0%);
}

.card.hoverable {
  transition: transform 0.1s ease-in-out;
}

.card.hoverable:hover {
  transform: translateY(-0.5rem) scale(1.0125);
  box-shadow: 0 .5rem 1rem rgba(0, 0, 0, .15) !important;
}
</style>
