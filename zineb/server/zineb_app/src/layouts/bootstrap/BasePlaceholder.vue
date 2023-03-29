<template>
  <span :class="placeholderClasses"></span>
</template>

<script>
export default {
  name: 'BasePlaceholder',
  props: {
    glow: {
      type: Boolean
    },
    wave: {
      type: Boolean,
      default: true
    },
    color: {
      type: String,
      default: 'dark'
    },
    size: {
      type: String,
      default: 'md'
    }
  },
  computed: {
    placeholderClasses () {
      return [
        'placeholder',
        {
          'placeholder-glow': this.glow,
          'placeholder-wave': this.wave,
          [`bg-${this.color}`]: true,
          [`placeholder-${this.size}`]: true
        }
      ]
    }
  }
}
</script>
