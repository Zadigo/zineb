<template>
  <input :id="id" :value="modelValue" :type="inputType" :name="id" :class="inputClasses" class="form-control" @input="emitValue($event)">

  <!-- <div class="b-slot">
    <div class="b-field-slot">
      <input :id="id" :value="modelValue" :type="inputType" :name="id" :class="inputClasses" class="form-control" @input="emitValue($event)">
    </div>
  </div> -->
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'BaseInput',
  props: {
    id: {
      type: String,
      required: true
    },
    inputType: {
      type: String,
      default: 'text'
    },
    modelValue: {
      type: [String, Number, Boolean]
    }
  },
  emits: {
    'update:modelValue' () {
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
    inputClasses () {
      return [
        {
          'bg-transparent text-light': this.darkMode
        }
      ]
    }
  },
  methods: {
    emitValue (e) {
      let value = e.target.value
      if (this.inputType === 'number') {
        value = value * 1
      }
      this.$emit('update:modelValue', value)
    }
  }
}
</script>

<style scoped>
.b-slot {
  align-items: center;
  display: flex;
  margin-bottom: 8px;
  min-height: inherit;
  position: relative;
  transition: .3s cubic-bezier(.25, .8, .5, 1);
  transition-property: height, min-height;
  width: 100%;
  border-radius: .25rem;
  cursor: text;
  padding: 0 12px;
  box-shadow: 0 .125rem .25rem rgba(0, 0, 0, .075) !important;
}

.b-field-slot {
  position: relative;
  display: flex;
  flex: 1 1 auto;
  align-items: center;
}

.b-field-slot input {
  flex: 1 1 auto;
  max-width: 100%;
  min-width: 0;
  width: 100%;
  max-height: 32px;
}

/* .b-field-slot .form-control:focus {
  border-color: inherit;
  box-shadow: none;
  outline: none;
  outline-style: none;
} */
</style>
