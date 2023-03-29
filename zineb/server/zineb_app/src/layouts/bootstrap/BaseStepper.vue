<template>
  <div class="stepper">
    <div class="wrapper">
      <div class="stepper horizontal">
        <div v-for="(item, i) in items" :key="i" :class="stepClasses(i)" class="step" @click="$emit('update:currentstep', i)">
          <div class="circle"><span>{{ i + 1 }}</span></div>
          <div class="title">{{ item.title }}</div>
          <div class="bar-left"></div>
          <div class="bar-right"></div>
        </div>
      </div>
    </div>  
  </div>
</template>

<script>
export default {
  name: 'BaseStepper',
  props: {
    items: {
      type: Array,
      default: () => []
    },
    currentStep: {
      type: Number,
      default: 0
    }
  },
  emits: {
    'update:currentstep' () {
      return true
    }
  },
  setup () {
    return {
    }
  },
  computed: {
  },
  methods: {
    stepClasses (step) {
      return [
        {
          'editable-step': step === this.currentStep, 
          'active-step': step <= this.currentStep, 
          'step-done': step < this.currentStep
        }
      ]
    }
  }
}
</script>

<style scoped>
.wrapper {
  width: 100%;
  padding: 0;
}

.stepper.horizontal {
  display: table;
  width: 100%;
  margin: 0 auto;
}

.stepper.horizontal .step {
  display: table-cell;
  position: relative;
  padding: 24px;
  cursor: pointer;
}

.stepper.horizontal .step:hover,
.stepper.horizontal .step:active {
  background-color: rgba(0, 0, 0, .06);
}

.stepper.horizontal .step:active {
  border-radius: 15% / 75%;
}

.stepper.horizontal .step:first-child:active {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.stepper.horizontal .step:last-child:active {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.stepper.horizontal .step:hover .circle {
  background-color: #757575;
}

.stepper.horizontal .step:first-child .bar-left,
.stepper.horizontal .step:last-child .bar-right {
  display: none;
}

.stepper.horizontal .step .circle {
  width: 24px;
  height: 24px;
  margin: 0 auto;
  background-color: #9E9E9E;
  border-radius: 50%;
  text-align: center;
  line-height: 2em;
  font-size: 12px;
  color: white;
}

.stepper.horizontal .step.active-step .circle {
  background-color: rgba(33, 150, 243, 1);
}

.stepper.horizontal .step.step-done .circle:before {
  content: "\2714";
}

.stepper.horizontal .step.step-done .circle *,
.stepper.horizontal .step.editable-step .circle * {
  display: none;
}

.stepper.horizontal .step.editable-step .circle {
  -moz-transform: scaleX(-1);
  /* Gecko */
  -o-transform: scaleX(-1);
  /* Opera */
  -webkit-transform: scaleX(-1);
  /* Webkit */
  transform: scaleX(-1);
  /* Standard */
}

.stepper.horizontal .step.editable-step .circle:before {
  content: "\270E";
}

.stepper.horizontal .step .title {
  margin-top: 16px;
  font-size: 14px;
  font-weight: normal;
}

.stepper.horizontal .step .title,
.stepper.horizontal .step .mdl-stepper-optional {
  text-align: center;
  color: rgba(0, 0, 0, .26);
}

.stepper.horizontal .step.active-step .title {
  font-weight: 500;
  color: rgba(0, 0, 0, .87);
}

.stepper.horizontal .step.active-step.step-done .title,
.stepper.horizontal .step.active-step.editable-step .title {
  font-weight: 300;
}

.stepper.horizontal .step .mdl-stepper-optional {
  font-size: 12px;
}

.stepper.horizontal .step.active-step .mdl-stepper-optional {
  color: rgba(0, 0, 0, .54);
}

.stepper.horizontal .step .bar-left,
.stepper.horizontal .step .bar-right {
  position: absolute;
  top: 36px;
  height: 1px;
  border-top: 1px solid #BDBDBD;
}

.stepper.horizontal .step .bar-right {
  right: 0;
  left: 50%;
  margin-left: 20px;
}

.stepper.horizontal .step .bar-left {
  left: 0;
  right: 50%;
  margin-right: 20px;
}
</style>
