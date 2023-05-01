<template>
  <div class="collapse-wrapper">
    <a :aria-expanded="show" :aria-controls="id" class="btn btn-primary" href role="button" @click.prevent="handleCollapse">
      {{ buttonName }}
    </a>

    <transition name="slide" mode="out-in">
      <div v-if="show" :id="id" :class="{ show }" class="collapse mt-1">
        <slot :dark-mode="darkMode"></slot>
      </div>
    </transition>
  </div>
</template>

<script>
import { inject, ref } from 'vue'

export default {
  name: 'BaseCollapse',
  props: {
    id: {
      type: String,
      required: true
    },
    buttonName: {
      type: String
    }
  },
  emits: {
    'collapse:update' () {
      return true
    }
  },
  setup () {
    const show = ref(false)
    const darkMode = inject('darkMode', false)
    return {
      darkMode,
      show
    }
  },
  methods: {
    handleCollapse () {
      this.show = !this.show
      this.$emit('collapse:update', this.show)
    }
  }
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all .45s ease-in-out;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-5%);
}
.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  transform: translateY(0%);
}
</style>
