<template>
  <div :id="id" :class="carouselClasses">
    <ol class="carousel-indicators">
      <li v-for="(item, i) in items" :key="item.id" :class="{ active: item.id === currentSlide.id }" :aria-current="item.id === currentSlide.id" :aria-label="`Slide ${i}`" @click="handleSelection(item)"></li>
    </ol>

    <div class="carousel-inner">
      <div class="view">
        <div v-for="item in items" :key="item.id" :class="{ active: item.id === currentSlide.id }" class="carousel-item">
          <img :src="item.url" :alt="item.alt" class="d-block w-100" />
          <div class="carousel-caption d-none d-md-block">
            <h5>{{ item.label }}</h5>
            <p>{{ item.description }}</p>
          </div>
        </div>
        <div class="mask rgba-black-strong"></div>
      </div>
    </div>

    <button class="carousel-control-prev" type="button" @click="handlePrevious">
      <font-awesome-icon icon="fa-solid fa-arrow-left" size="1x" />
      <span class="visually-hidden">Previous</span>
    </button>
    
    <button class="carousel-control-next" type="button" @click="handleNext">
      <font-awesome-icon icon="fa-solid fa-arrow-right" size="1x" />
      <span class="visually-hidden">Next</span>
    </button>
  </div>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'BaseCarousel',
  props: {
    id: {
      type: String,
      required: true
    },
    items: {
      type: Array,
      default: () => []
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
      currentId: 0,
      index: 0
    }
  },
  computed: {
    currentSlide () {
      const items = this.items.filter((image) => {
        return image.id === this.currentId
      })
      return items[0]
    },
    carouselClasses () {
      return [
        'carousel slide carousel-fade',
        {
          'carousel-dark': this.darkMode
        }
      ]
    }
  },
  created () {
    this.currentId = this.items[0].id
  },
  methods: {
    handleSelection (item) {
      this.currentId = item.id
    },
    handlePrevious () {
      let index = this.index - 1
      if (index < 0) {
        index = this.items.length - 1
      }
      this.index = index
      this.currentId = this.items[index].id
    },
    handleNext () {
      let index = this.index + 1
      if (index >= this.items.length) {
        index = 0
      }
      this.index = index
      this.currentId = this.items[index].id
    }
  }
}
</script>

<style scoped>
.carousel-indicators {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 2;
  display: flex;
  justify-content: center;
  padding: 0;
  margin-right: 15%;
  margin-bottom: 1rem;
  margin-left: 15%;
  list-style: none;
}

.carousel-indicators li {
  box-sizing: content-box;
  flex: 0 1 auto;
  width: 30px;
  height: 3px;
  padding: 0;
  margin-right: 3px;
  margin-left: 3px;
  text-indent: -999px;
  cursor: pointer;
  background-color: #fff;
  background-clip: padding-box;
  border: 0;
  border-top: 10px solid transparent;
  border-bottom: 10px solid transparent;
  opacity: .5;
  transition: opacity .6s ease;
}

.carousel-indicators .active {
  opacity: 1;
}
</style>
