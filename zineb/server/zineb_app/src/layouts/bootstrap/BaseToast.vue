<template>
  <!-- bottom-0 end-0 -->
  <div class="toast-container position-fixed top-0 end-0 p-3">
    <div :class="{ show }" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
      <div :class="{ 'bg-dark text-white': darkMode }" class="toast-header">
        <!-- <img src="" class="rounded me-2" alt="..."> -->
        <strong class="me-auto">Bootstrap</strong>
        <small>11 mins ago</small>
        <button type="button" class="btn-close" aria-label="Close" @click="$emit('close'), show = !show"></button>
      </div>

      <div :class="{ 'bg-dark text-white': darkMode }" class="toast-body">
        {{ item.text }}
      </div>
    </div>
  </div>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'BaseToast',
  props: {
    item: {
      type: Object,
      default () {
        return {}
      }
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
  data () {
    return {
      show: true,
      internalToast: {},
    }
  },
  mounted () {
    // this.$refs.link.addEventListener('')
  }
  // watch: {
  //   show (current) {
  //     if (current) {
  //       setTimeout(() => {
  //         this.show = false
  //       }, 3000)
  //     }
  //   }
  // }
}
</script>



<style scoped>
.toast-container {
  z-index: 1000;
}
</style>
