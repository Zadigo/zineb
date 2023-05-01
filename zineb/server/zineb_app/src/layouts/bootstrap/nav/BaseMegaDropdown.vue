<template>
  <li class="nav-item dropdown has-megamenu">
    <!-- @mouseenter="show=true, $emit('show', true)" -->
    <a ref="link" :class="{ show }" :aria-expanded="show" class="nav-link dropdown-toggle" href @click.prevent="show=true, $emit('click', show)">
      Mega menu
    </a>

    <div v-if="show" class="screen-darken"></div>

    <div ref="megamenu" :class="dropdownClasses" class="dropdown-menu megamenu" role="menu" @mouseleave="show=false, $emit('show', false)">
      <div class="row g-3">
        <div v-for="(item, x) in items" :key="x" class="col-lg-3 col-6">
          <div class="col-megamenu">
            <h6 class="title text-uppercase fw-bold p-1 m-0">
              {{ item.title }}
            </h6>

            <ul class="list-unstyled p-1">
              <li v-for="(link, y) in item.links" :key="y" class="my-2">
                <a href="#">{{ link.name }}</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </li>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'BaseMegaDropdown',
  props: {
    items: {
      type: Array,
      required: true
    }
  },
  emits: {
    'click' () {
      return true
    },
    'show' () {
      return true
    }
  },
  setup () {
    const darkMode = inject('darkMode', false)
    return {
      darkMode
    }
  },
  data () {
    return {
      show: false
    }
  },
  computed: {
    dropdownClasses () {
      return [
        this.show ? 'show' : null,
        this.darkMode ? 'bg-dark text-light' : 'bg-white text-dark'
      ]
    }
  }
}
</script>

<style scoped>
.screen-darken {
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  transition: all .3s ease;
  background-color: rgba(0, 0, 0, .5);
  filter: blur(1px);
  z-index: 1;
}

.bg-dark li>a {
  color: #fff;
}

.bg-white li>a {
  color: rgb(33, 37, 41);
}
</style>
