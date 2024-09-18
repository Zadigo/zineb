<template>
  <!-- style="position: absolute; inset: 0px 0px auto auto; margin: 0px; transform: translate(0px, 40px);" -->
  <!-- dropdown-menu-end show -->
  <transition :name="animation" mode="in-out">
    <ul v-if="show" :class="dropMenuClasses" class="dropdown-menu mt-2" aria-labelledby="navbarDropdownMenuLink">
      <slot></slot>
    </ul>  
  </transition>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'DropdownMenu',
  props: {
    animation: {
      type: String,
      default: 'slide'
    },
    padding: {
      type: Number,
      default: 2
    },
    show: {
      type: Boolean
    }
  },
  emits: {
    'open:dropdown-menu' () {
      return true
    },
    'close:dropdown-menu' () {
      return true
    },
    'click:dropdown-menu' () {
      return true
    }
  },
  setup () {
    const darkMode = inject('darkMode', false)
    return {
      darkMode
    }
  },
  computed: {
    dropMenuClasses () {
      return [
        {
          [`p-${this.padding}`]: true,
          show: this.show,
          'dropdown-menu-dark': this.darkMode
        }
      ]
    }
  },
  watch: {
    show (current) {
      if (current) {
        this.$emit('open:dropdown-menu')
      } else {
        this.$emit('close:dropdown-menu')
      }
    }
  },
}
</script>

<style scoped>
.scale-enter-active,
.scale-leave-active {
  position: absolute;
  transition: all .3s ease;
  margin: 0px;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(.9, .9);
}

.scale-enter-to,
.scale-leave-from {
  opacity: 1;
  transform: scale(1, 1);
}

.slide-enter-active,
.slide-leave-active {
  position: absolute;
  transition: all .3s ease;
  margin: 0px;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(-15px);
}

.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  transform: translateX(0px);
}

.slideup-enter-active,
.slideup-leave-active {
  position: absolute;
  transition: all .3s ease;
  margin: 0px;
}

.slideup-enter-from,
.slideup-leave-to {
  opacity: 0;
  transform: translateY(15px);
}

.slideup-enter-to,
.slideup-leave-from {
  opacity: 1;
  transform: translateY(0px);
}

.dropdown-item.active,
.dropdown-item:active {
  color: #fff;
  text-decoration: none;
  background-color: #0d6efd;
}
</style>

}
