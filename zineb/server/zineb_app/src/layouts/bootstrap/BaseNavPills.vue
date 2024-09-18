<template>
  <div class="wrapper">
    <ul :class="navpillClasses">
      <li class="nav-item">
        <a v-for="(item, i) in items" :key="i" :aria-current="i == selectedTab" :class="{ active: i === selectedTab }" class="nav-link" href @click.prevent="selectItem(i, item)">
          {{ item.name }}
        </a>
      </li>
    </ul>
    
    <transition name="slide" mode="out-in">
      <slot :selected-tab="selectedTab"></slot>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'NavPills',
  props: {
    items: {
      type: Array,
      default () {
        return []
      }
    },
    position: {
      type: String
    },
    horizontal: {
      type: Boolean,
      default: true
    },
    isTabs: {
      type: Boolean
    },
    isPills: {
      type: Boolean
    },
    justified: {
      type: Boolean
    },
    fill: {
      type: Boolean
    },
    pillClasses: {
      type: Object,
      default () {
        return {}
      }
    },
    inCard: {
      type: Boolean
    }
  },
  emits: {
    change () {
      return true
    },
    'click:nav-pill' () {
      return true
    }
  },
  data () {
    return {
      selectedTab: 0
    }
  },
  computed: {
    currentTab () {
      return this.items[this.selectedTab]
    },
    navpillClasses () {
      return [
        'nav',
        this.pillClasses,
        {
          'justify-content-center': this.position === 'center',
          'justify-content-end': this.position === 'end',
          'flex-column': !this.horizontal,
          'nav-tabs': this.isTabs,
          'nav-pills': this.isPills,
          'nav-fill': this.fill,
          'nav-justified': this.justified,
          'card-header-tabs': this.isPills && this.inCard,
          'card-header-pills': this.isTabs && this.inCard
        }
      ]
    }
  },
  watch: {
    selected (current, previous) {
      this.$emit('change', { current: current, previous: previous })
    }
  },
  methods: {
    selectItem (index, item) {
      this.selectedTab = index
      this.$emit('click:nav-pill', [index, item])
    }
  }
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all .3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(100px);
}

.slide-leave-to,
.slide-enter-to {
  opacity: 1;
  transform: translateX(0px);
}
</style>
