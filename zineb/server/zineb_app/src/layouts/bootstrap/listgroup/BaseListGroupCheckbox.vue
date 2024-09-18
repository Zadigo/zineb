<template>
  <div :id="id" class="list-group mx-0 w-auto">
    <label v-for="(item, i) in items" :key="i" :class="{ 'text-bg-dark': darkMode }" class="list-group-item d-flex gap-2">
      <input :id="`${id}-${i}`" :checked="isSelected(i)" :disabled="item.disabled" :value="i" :name="`${id}-1`" class="form-check-input flex-shrink-0" type="checkbox" @click="selectItem($event, i), $emit('list-group-selection', selectedByIndex)">
      <span>
        {{ item.name }}
        <small v-if="item.subtitle" class="d-block text-muted">{{ item.subtitle }}</small>
      </span>
    </label>
  </div>
</template>

<script>
import { getCurrentInstance, inject } from 'vue'
import { useLists } from '../composables/index'

export default {
  name: 'BaseListGroupCheckbox',
  props: {
    id: {
      type: String,
      required: true
    },
    items: {
      type: Array,
      required: true
    }
    // isRadio: {
    //   type: Booleean
    // }
    // initial: {
    //   type: Array,
    //   default: true
    // }
  },
  emits: {
    'list-group-selection' () {
      return true
    }
  },
  setup () {
    const app = getCurrentInstance()
    const { selected, selectItem, isSelected, selectedByIndex } = useLists(app.props.items)
    const darkMode = inject('darkMode', false)
    return {
      selected,
      selectItem,
      darkMode,
      isSelected,
      selectedByIndex
    }
  }
}
</script>
