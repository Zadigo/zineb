<template>
  <ul class="nav nav-pills">
    <li v-for="(item, i) in items" :key="i" class="nav-item">
      <router-link v-if="item.to" :to="item.to" aria-current="page">
        {{ item.name }}
      </router-link>

      <a v-else :class="{active: i === currentTab}" class="nav-link" href @click.prevent="setTab(i)">
        {{ item.name }}
      </a>
    </li>
  </ul>
</template>

<script>
export default {
  name: 'BaseNavPills',
  props: {
    items: {
      type: Array,
      default: () => []
    }
  },
  emits: {
    'current-tab' () {
      return true
    }
  },
  data () {
    return {
      currentTab: 0
    }
  },
  methods: {
    setTab (index) {
      this.currentTab = index
      this.$emit('current-tab', index)
    }
  }
}
</script>
