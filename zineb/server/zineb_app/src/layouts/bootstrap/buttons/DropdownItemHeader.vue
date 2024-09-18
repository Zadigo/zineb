<template>
  <li>
    <h6 class="dropdown-header">
      {{ linkName }}
    </h6>
  </li>
</template>


<script>
export default {
  name: 'DropdownItemHeader',
  props: {
    linkName: {
      type: String,
      required: true
    }
  }
}
</script>
