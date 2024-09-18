<template>
  <li>
    <a :class="dropdownItemClasses" href @click.prevent="$emit('click:dropdown-item', linkName)">
      <font-awesome-icon :icon="`fa-solid fa-${icon}`" />
      <span><slot>{{ linkName }}</slot></span>
    </a>
  </li>
</template>


<script>
export default {
  name: 'DropdownItem',
  props: {
    icon: {
      type: String,
      default: null
    },
    linkName: {
      type: String,
    },
    active: {
      type: Boolean 
    },
    disabled: {
      type: Boolean
    }
  },
  emits: {
    'click:dropdown-item' () {
      return true
    }
  },
  computed: {
    dropdownItemClasses () {
      return [
        'dropdown-item',
        {
          'd-flex gap-2 align-items-center': this.icon !== null,
          active: this.active,
          disabled: this.disabled
        }
      ]
    }
  }
}
</script>
