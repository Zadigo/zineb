<template>
  <form class="mb-2" @submit.prevent="handleSubmit">
    <input v-model="value" type="search" class="form-control dropdown-input" autocomplete="false" placeholder="Type to filter...">
  </form>
</template>


<script>
export default {
  name: 'DropdownItemInput',
  props: {
    linkName: {
      type: String,
      required: true
    }
  },
  emits: {
    'update:dropdown-input' () {
      return true
    },
    'click:dropdown-item' () {
      return true
    }
  },
  data () {
    return {
      value: null
    }
  },
  methods: {
    handleSubmit () {
      this.$emit('update:dropdown-input', this.value)
      this.$emit('click:dropdown-item', this.linkName)
      this.value = null
    }
  }
}
</script>
