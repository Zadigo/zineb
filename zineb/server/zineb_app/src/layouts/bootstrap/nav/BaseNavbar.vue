<template>
  <nav ref="link" :class="navbarClasses" class="navbar navbar-expand-lg">
    <div :class="containerFluid ? 'container-fluid' : 'container'">
      <router-link to="/" class="navbar-brand fw-bold text-uppercase">
        {{ navBrand }}
      </router-link>

      <button :class="{ collapsed }" type="button" class="navbar-toggler" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation" @click="collapsed = !collapsed">
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div id="navbarNav" :class="{'collapse show': !collapsed}" class="collapse navbar-collapse">
        <slot></slot>
      </div>
    </div>
  </nav>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'BaseNavbar',
  props: {
    containerFluid: {
      type: Boolean
    },
    fixedTop: {
      type: Boolean
    },
    navBrand: {
      type: String,
      required: true
    }
  },
  setup () {
    const height = 0
    const darkMode = inject('darkMode', false)
    return {
      height,
      darkMode
    }
  },
  data () {
    return {
      collapsed: true
    }
  },
  computed: {
    navbarClasses () {
      return [
        {
          'fixed-top': this.fixedTop
        },
        // 'bg-transparent navbar-dark'
        // 'bg-transparent navbar-dark shadow-none'
        this.darkMode ? 'navbar-dark bg-dark' : 'navbar-light bg-white'
      ]
    }
  },
  mounted () {
    this.height = this.$refs.link.offsetHeight
    // if (this.fixedTop) {
    //   this.$refs.link.style.marginBottom = `${this.height - 5}px`
    // }
  }
}
</script>

<style scoped>
.navbar-collapse {
  transition: all .3s ease;
  animation: collapsing .4s cubic-bezier(0.075, 0.82, 0.165, 1);
}

@keyframes collapsing {
  0% {
    height: 50%;
  }
  
  99% {
    height: 100%;
  }
}
</style>
