<template>
  <ul :class="listGroupClasses" class="list-group">
    <slot :handle-selection="handleSelection" :list-group-items="listGroupItems"></slot>
  </ul>
</template>

<script>
// import { ref, getCurrentInstance } from 'vue'
// import { useLists } from '../composables/index'

export default {
  name: 'BaseListGroup',
  props: {
    color: {
      type: Boolean,
      default: null
    },
    horizontal: {
      type: Boolean
    },
    flush: {
      type: Boolean
    },
    numbered: {
      type: Boolean
    },
    items: {
      type: Array,
      default: () => []
    }
  },
  emits: {
    'update:list-group-selection' () {
      return true
    }
  },
  // setup () {
  //   const app = getCurrentInstance()
  //   const listGroupItems = app.props.items
  //   const lastSelection = ref({})
  //   const { selectedByIndex, simpleSelection, selected } = useLists(listGroupItems)
  //   return {
  //     lastSelection,
  //     simpleSelection,
  //     listGroupItems,
  //     selected,
  //     selectedByIndex
  //   }
  // },
  computed: {
    listGroupItems () {
      return this.items
    },
    listGroupClasses () {
      return [
        {
          'list-group-flush': this.flush,
          'list-group-numbered': this.numbered,
          'list-group-horizontal': this.horizontal,
          [`list-group-item-${this.color}`]: true
        }
      ]
    }
  },
  methods: {
    handleSelection (index) {
      this.lastSelection = this.items[index]
      this.simpleSelection(index)
      this.$emit('update:list-group-selection', this.selectedByIndex)
    }
  }
}
</script>
