<template>
  <div class="dropdown">
    <base-button :id="id" :size="size" :aria-expanded="show" class="dropdown-toggle" type="button" @click="show = !show">
      {{ linkName }}
    </base-button>
    
    <!-- <base-drop-menu :show="show" @click:dropdown-item="show = !show" /> -->
    <slot :show="show" @click:dropdown-item="handleClick"></slot>
  </div>
</template>

<script>
import { useClickOutside } from '../composables'

import BaseButton from './BaseButton.vue'

export default {
  name: 'BaseDropdownButton',
  components: {
    BaseButton
  },
  props: {
    id: {
      type: String,
      required: true
    },
    size: {
      type: String,
      default: 'md'
    },
    linkName: {
      type: String,
      required: true
    }
  },
  setup () {
    const { show, handleClick } = useClickOutside()
    return {
      show,
      handleClick
    }
  }
}
</script>
