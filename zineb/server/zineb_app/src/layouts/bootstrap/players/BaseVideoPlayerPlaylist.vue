<template>
  <div class="video-playlist">
    <slot :video-url="currentVideo" @update:state="increase" @show-playlist="showDrawer=!showDrawer"></slot>

    <aside v-if="showDrawer">
      <div v-for="(video, i) in playlist" :key="video" :class="{selected: i===index}" class="preview mb-1" @click="select(i)">
        <img src="https://via.placeholder.com/400x400" class="img-fluid" alt="">
      </div>
    </aside>
  </div>
</template>

<script>
export default {
  name: 'BaseVideoPlayerPlaylist',
  props: {
    playlist: {
      type: Array,
      // {name, url, created_on}
      default: () => []
    }
  },
  emits: {
    'update:video-url' () {
      return true
    }
  },
  data () {
    return {
      index: 0,
      showDrawer: true
    }
  },
  computed: {
    numberOfVideos () {
      return this.playlist.length
    },
    previousVideo () {
      const result = this.index - 1
      if (result < 0) {
        return this.playlist[0]
      }
      return this.playlist[result]
    },
    currentVideo () {
      return this.playlist[this.index]
    }
  },
  methods: {
    increase () {
      let result = this.index + 1
      if (result > this.numberOfVideos) {
        result = this.numberOfVideos
      }
      this.$emit('update:video-url', this.currentVideo)
      return result
    },
    decrease () {
      let result = this.index - 1
      if (result < 0) {
        result = this.numberOfVideos
      }
      this.$emit('update:video-url', this.currentVideo)
      return result
    },
    select (index) {
      this.index = index
      this.$emit('update:video-url', this.currentVideo)
    }
  }
}
</script>

<style scoped>
.video-playlist {
  position: relative;
  overflow: hidden;
}

aside {
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  width: 15%;
  height: 100%;
  z-index: 1055;
  padding: 1rem;
  background-color: white;
  overflow-y: scroll;
}

.preview {
  width: 100%;
  max-width: 100%;
  cursor: pointer;
}

.preview.selected {
  border: 2px solid rgba(38, 38, 38, 0.375);
}

aside::-webkit-scrollbar {
  display: none;
}
</style>
