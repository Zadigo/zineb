<template>
  <div :class="[isSwitch ? 'form-switch' : 'form-check', { 'form-check-inline': inline }]">
    <input :id="id" :class="inputClasses" :checked="modelValue" :type="checkboxType" :role="[isSwitch ? 'switch' : null]" :name="name" class="form-check-input" @change="emitValue($event)">
    <label :for="id" class="form-check-label">{{ label }}</label>
  </div>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'BaseCheckbox',
  props: {
    id: {
      type: String,
      required: true
    },
    // bigger: {
    //   type: Boolean
    // },
    inline: {
      type: Boolean
    },
    isSwitch: {
      type: Boolean,
      default: false
    },
    isRadio: {
      type: Boolean,
      default: false
    },
    modelValue: {
      type: Boolean
    },
    label: {
      type: String,
      required: true
    },
    name: {
      type: String
    }
  },
  emits: {
    'update:modelValue' () {
      return true
    }
  },
  setup () {
    const darkMode = inject('darkMode', () => false)
    return {
      darkMode
    }
  },
  computed: {
    inputClasses () {
      return [
        // {
        //   'fs-input-bigger': this.bigger && !this.isSwitch,
        // },
        {
          dark: this.darkMode
        }
      ]
    },
    checkboxType () {
      if (this.isSwitch && this.isRadio) {
        return 'checkbox'
      } else if (this.isSwitch) {
        return 'checkbox'
      } else if (this.isRadio) {
        return 'radio'
      } else {
        return 'checkbox'
      }
    }
  },
  methods: {
    emitValue (e) {
      // https://stackoverflow.com/questions/70515367/passing-v-model-into-a-checkbox-inside-a-component-in-vue-3
      this.$emit('update:modelValue', e.target.checked)
    }
  }
}
</script>

<style scoped>
.form-check-input.fs-input-bigger {
  font-size: 1.375em;
}
</style>
