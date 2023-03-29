<template>
  <div class="btn-group">
    <base-button :id="id">{{ linkName }}</base-button>
    
    <base-button :aria-expanded="show" class="btn btn-primary dropdown-toggle dropdown-toggle-split" @click="show = !show">
      <span class="visually-hidden">Toggle Dropdown</span>
    </base-button>
    
    <slot :show="show"></slot>
  </div>
</template>

<script>
import { useClickOutside } from '../composables'

import BaseButton from './BaseButton.vue'

export default {
  name: 'TestBaseDropdownButton',
  components: {
    BaseButton
  },
  props: {
    id: {
      type: String,
      required: true
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
