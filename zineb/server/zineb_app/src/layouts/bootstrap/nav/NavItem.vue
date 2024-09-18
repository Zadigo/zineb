<template>
  <li class="nav-item">
    <a v-if="href" :href="href" class="nav-link">{{ linkName }}</a>
    <router-link v-else :to="to" class="nav-link">
      {{ linkName }}
    </router-link>
  </li>
</template>

<script>
export default {
  name: 'NavItem',
  props: {
    to: {
      type: Object,
      required: true
    },
    href: {
      type: String,
      default: null
    },
    linkName: {
      type: String,
      required: true
    }
  }
}
</script>
