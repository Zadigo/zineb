import _ from 'lodash'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

export function useClickOutside (onbefore = () => { }, onafter = () => { }) {
  // Handle menu state when click outside
  const show = ref(false)
  
  function handleButtonClickOutside (e) {
    const target = e.target

    onbefore(e)

    if (target.classList.contains('dropdown-header')) {
      return
    }
    
    if (target.classList.contains('dropdown-input')) {
      return
    }

    if (target.classList.contains('dropdown-divider')) {
      return
    }

    if (!target.classList.contains('dropdown-toggle')) {
      show.value = false
    }
    
    onafter(e)
  }

  function handleClick() {
    show.value = !show.value
  }

  onMounted(() => {
    window.addEventListener('click', handleButtonClickOutside)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('click', handleButtonClickOutside)
  })

  return {
    show,
    handleClick
  }
}

export function useLists (items, onbefore = () => { }, onafter = () => { }) {
  const _items = items
  const selected = ref([])

  function selectionManager (item) {
    // Manage the items in the selection list
    if (selected.value.includes(item)) {
      const index = _.indexOf(selected.value, item)
      selected.value.splice(index, 1)
    } else {
      selected.value.push(item)
    }
  }

  function selectItem (e, index) {
    onbefore(e)
    selectionManager(index)
    onafter(e)
  }

  function simpleSelection (index) {
    // Select items without passing
    // the event object
    selectionManager(index)
  }
  
  function isSelected (index) {
    // Checks if an item is selected
    return selected.value.includes(index)
  }

  // const selectedById = computed(() => {
  //   return selected.value.map((id) => {
  //     return _items.id === id
  //   })
  // })

  const selectedByIndex = computed(() => {
    // Return the list of selected items by
    // their position in the list
    return selected.value.map((index) => {
      return _items[index]
    })
  })
  
  return {
    isSelected,
    selected,
    // selectedById,
    selectedByIndex,
    selectItem,
    simpleSelection
  }
}

export function useEventListener (el, event, callback) {
  onMounted(() => {
    el?.value?.addEventListener(event, callback)
  })

  onBeforeUnmount(() => {
    el?.value?.removeEventListener(event, callback)
  })
}

export function useUtilities () {
  // Generate a random ID for a component
  // for cases where the user has not
  // provided one
  function generateId (suffix) {
    return `__BID__${Math.random().toString().slice(2, 8)}___B_${suffix}__`
  }

  return {
    generateId
  }
}
