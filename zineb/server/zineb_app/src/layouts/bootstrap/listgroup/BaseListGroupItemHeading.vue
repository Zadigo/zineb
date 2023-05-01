<template>
  <div class="ms-2 me-auto">
    <div class="fw-bold">{{ item.title }}</div>
    {{ item.subtitle }}
  </div>
</template>

<script>
export default {
  name: 'BaseListGroupItemHeading',
  props: {
    item: {
      type: Object,
      default () {
        return {}
      }
    }
  }
}
</script>
