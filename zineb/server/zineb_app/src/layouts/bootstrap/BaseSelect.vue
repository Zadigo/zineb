<template>
  <select v-model="value" class="form-select">
    <option v-for="(item, i) in items" :key="i">
      {{ item }}
    </option>
  </select>

  <div v-show="false" :class="{ expanded: showSelections }" class="b-group" @click="showSelections = !showSelections">
    <div role="button" :aria-expanded="showSelections" class="b-slot">
      <div class="b-outer">
        <div class="b-icon-prepend">
          <font-awesome-icon icon="fa-solid fa-table"></font-awesome-icon>
        </div>
      </div>

      <div class="b-select">
        <div class="b-selections">
          <!-- <span class="b-chip">
            <div class="b-chip-content">Google</div>
          </span> -->
          <input :value="value" readonly="true" type="text" aria-readonly="false" autocomplete="off" class="form-control">
        </div>
        
        <!-- Append -->
        <div class="b-inner">
          <div class="b-icon-append">
            <font-awesome-icon icon="fa-solid fa-arrow-right"></font-awesome-icon>
          </div>
        </div>
        
        <input v-model="value" type="hidden">
      </div>
    </div>

    <transition name="menu-slideup">
      <ul v-if="showSelections" :class="{ show: showSelections }" class="dropdown-menu">
        <li v-for="item in items" :key="item">
          <a href class="dropdown-item" @click.prevent="value = item">
            {{ item }}
          </a>
          <!-- <a href class="dropdown-item d-flex align-items-center gap-2 justify-content-left" @click.prevent="value = item">
            <div class="form-check">
              <input type="checkbox" class="form-check-input">
            </div>
            <span>{{ item }}</span>
          </a> -->
        </li>
      </ul>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'BaseSelect',
  props: {
    items: {
      type: Array
    },
    modelValue: {
      type: String
    }
  },
  emits: {
    'update:modelValue' () {
      return true
    }
  },
  data () {
    return {
      showSelections: false
    }
  },
  computed: {
    value: {
      get () {
        return this.modelValue
      },
      set (value) {
        return this.$emit('update:modelValue', value)
      }
    }
  },
  methods: {
    
  }
}
</script>

<style scoped>
.b-group {
  position: relative;
  display: flex;
  flex-direction: column;
  height: auto;
  flex-grow: 1;
  flex-wrap: wrap;
  min-width: 0;
  width: 100%;

  min-height: 48px;
  padding: 0;
  
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.6;
  color: #4f4f4f;
}

.b-group.expanded .b-icon {
  transform: rotate(90deg);
}

.b-slot {
  align-items: center;
  display: flex;
  margin-bottom: 8px;
  min-height: inherit;
  position: relative;
  transition: .3s cubic-bezier(.25, .8, .5, 1);
  transition-property: height, min-height;
  width: 100%;
  cursor: pointer;
  border-radius: .25em;
  padding: 0 12px;
  box-shadow: 0 .125rem .25rem rgba(0, 0, 0, .075) !important;
}

.b-select {
  position: relative;
  align-items: center;
  display: flex;
  max-width: 100%;
  min-width: 0;
  width: 100%;
}

.b-selections {
  align-items: center;
  display: flex;
  flex: 1 1;
  flex-wrap: wrap;
  line-height: 18px;
  max-width: 100%;
  min-width: 0;
}

.b-group input {
  position: relative;
  flex: 1 1 auto;
  max-width: 100%;
  min-width: 0;
  width: 100%;
  max-height: 32px;
  /* border: none; */
}

.b-outer {
  display: inline-flex;
  margin-bottom: 4px;
  margin-top: 4px;
  line-height: 1;
}

.b-inner {
  display: inline-flex;
  align-self: center;
  margin-top: 0;
}

.b-icon-prepend,
.b-icon-append {
  align-items: center;
  display: inline-flex;
  height: 24px;
  min-width: 24px;
  flex: 1 0 auto;
  justify-content: center;
  width: 24px;
}

.dropdown-menu {
  position: absolute;
  width: 100%;
  margin-top: calc(48px + .5rem);
  padding: .5rem;
}

.b-chip {
  align-items: center;
  cursor: default;
  display: inline-flex;
  line-height: 20px;
  max-width: 100%;
  outline: none;
  overflow: hidden;
  padding: 0 12px;
  position: relative;
  text-decoration: none;
  transition-duration: .28s;
  transition-property: box-shadow, opacity;
  transition-timing-function: cubic-bezier(.4, 0, .2, 1);
  vertical-align: middle;
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
  flex: 0 1 auto;
  margin: 4px;
  background: #e0e0e0;
  border-radius: 16px;
  font-size: 14px;
  height: 32px;
}

.b-chip-content {
  display: inline-flex;
  align-items: center;
  height: 100%;
  max-width: 100%;
}

.b-group .form-control:focus {
  border-color: inherit;
  box-shadow: none;
  outline: none;
  outline-style: none;
}

.b-group .form-control[readonly] {
  background-color: #fff;
}
</style>
