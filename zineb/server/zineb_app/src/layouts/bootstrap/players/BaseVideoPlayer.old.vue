<template>
  <div class="video__container" @click="toggleVideoPlay" @mouseover="handleShowFunctions" @mouseleave="setTimeoutFunction">
    <div v-if="spinner" class="spinner">
      <!-- <v-progress-circular indeterminate color="var(--primary-color)"></v-progress-circular> -->
      <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Source -->
    <video ref="videoPlayer" class="video__player" controlslist="nodownload" oncontextmenu="return false;" @loadedmetadata="updateVideoDetails" @timeupdate="updateVideoDetails" @waiting="spinner = true" @canplay="spinner = false">
      <source :src="videoSrc" type="video/mp4" />
    </video>

    <!-- Controls -->
    <div v-if="showProgressBar" class="video__controls">
      <div class="video__controls__progress__container" :style="`margin-bottom:${showFunctions ? '20px' : '0'}`">
        <div ref="videoPlayerProgress" class="video__controls__progress" @click.prevent.stop="handleProgressClick">
          <div class="video__controls__progress__track" :style="{ width: progress + '%' }">
            <div :style="{ left: progress + '%' }" class="video__controls__progress__track--watching" draggable @drag.stop.prevent="handleTrackOnDrag"></div>
          </div>
        </div>
      </div>

      <div v-if="showFunctions" class="video__controls__functions">
        <div>
          <button type="button" class="video__controls__button btn btn-light" @click.stop="toggleVideoPlay">
            <!-- <v-icon v-if="isPlaying" style="color: #fff">mdi-pause</v-icon> -->
            <!-- <v-icon v-else style="color: #fff">mdi-play</v-icon> -->
            <span v-if="isPlaying" class="mdi mdi-pause"></span>
            <span v-else class="mdi mdi-play"></span>
          </button>

          <div class="video__controls__duration">
            <span>{{ currentTimeFormatted }}</span>/
            <span>{{ durationFormatted }}</span>
          </div>
        </div>

        <div class="video__controls__configs">
          <div class="video__controls__volume">
            <button ref="volumeTrack" type="button" class="btn btn-light" @click.stop="volumeOptionsOpen = !volumeOptionsOpen">
              <!-- <v-icon v-if="volume < 0.1" style="color: #fff">mdi-volume-low</v-icon>
              <v-icon v-else-if="volume >= 0.1 && volume < 0.8" style="color: #fff">mdi-volume-medium</v-icon>
              <v-icon v-else-if="volume >= 0.8" style="color: #fff">mdi-volume-high</v-icon> -->
              <span v-if="volume < 0.1" class="mdi mdi-volume-low"></span>
              <span v-else-if="volume >= 0.1 && volume < 0.8" class="mdi mdi-volume-medium"></span>
              <span v-else-if="volume >= 0.8" class="mdi mdi-volume-high"></span>
            </button>

            <div v-if="volumeOptionsOpen" ref="videoVolumeTrack" class="video__controls__volume--options" @click.stop="handleVolumeClick">
              <div class="video__controls__volume--track">
                <div class="video__controls__volume--track-current" :style="{ height: `${volume * 100}%` }" />

                <div class="video__controls__volume--track-ball" :style="{ bottom: `Calc(${volume * 100}% - 0.25rem)` }" />
              </div>
            </div>
          </div>

          <div class="video__controls__speed">
            <button ref="speed" type="button" class="btn btn-light" @click.stop="speedOpen = !speedOpen">
              <span>
                <!-- <v-icon style="color: #fff">mdi-speedometer</v-icon> -->
                <span class="mdi mdi-speedometer"></span>
              </span>
            </button>

            <div v-if="speedOpen" class="video__controls__speed__options">
              <div :class="{ active: !!(speed === '2x') }" @click.stop="handleVideoPlaybackRate(2.0)">2x</div>
              <div :class="{ active: !!(speed === '1.75x') }" @click.stop="handleVideoPlaybackRate(1.75)">1.75x</div>
              <div :class="{ active: !!(speed === '1.5x') }" @click.stop="handleVideoPlaybackRate(1.5)">1.5x</div>
              <div :class="{ active: !!(speed === '1x') }" @click.stop="handleVideoPlaybackRate(1.0)">1x</div>
              <div :class="{ active: !!(speed === '0.75x') }" @click.stop="handleVideoPlaybackRate(0.75)">0.75x</div>
              <div :class="{ active: !!(speed === '0.5x') }" @click.stop="handleVideoPlaybackRate(0.5)">0.5x</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseVideoPlayer',
  props: {
    videoUrl: {
      type: String,
      required: true,
    },
  },
  emits: ['play', 'pause', 'player-ready', 'dragged', 'progress'],
  data: () => ({
    volumeOptionsOpen: false,
    volume: 0.3,
    isPlaying: false,
    duration: 0,
    currentTime: 0,
    speed: "1x",
    speedOpen: false,
    videoSrc: null,
    spinner: true,
    showFunctions: false,
    timeout: null,
    showProgressBar: true
  }),
  computed: {
    currentTimeFormatted () {
      return this.formatTime(this.currentTime);
    },

    durationFormatted () {
      return this.formatTime(this.duration);
    },
    
    progress () {
      return (this.currentTime / this.duration) * 100;
    }
  },
  watch: {
    videoUrl (val) {
      if (!!val && val !== this.videoSrc) {
        this.videoSrc = val;
        this.$forceUpdate();
      }
    },
  },
  mounted () {
    this.updateVideoDetails()
    this.videoSrc = this.videoUrl
  },
  methods: {
    toggleVideoPlay () {
      if (this.$refs?.videoPlayer.paused) {
        this.isPlaying = true
        this.$refs.videoPlayer.play()

        this.$emit('play')
      } else {
        this.isPlaying = false
        this.$refs.videoPlayer.pause()
        
        this.$emit('pause', this.progress)
      }
    },
    handleVolumeClick (event) {
      const volume = this.$refs.videoVolumeTrack
      const currentVolume = (volume.getBoundingClientRect().top - event.pageY + volume.offsetHeight) / 100

      if (currentVolume > 1) {
        this.volume = currentVolume
        this.$refs.videoPlayer.volume = 1
      } else if (currentVolume < 0.1) {
        this.volume = 0
        this.$refs.videoPlayer.volume = 0
      } else {
        this.volume = currentVolume
        this.$refs.videoPlayer.volume = currentVolume
      }
    },
    updateVideoDetails () {
      if (this.$refs.videoPlayer) {
        if (!Number.isNaN(this.$refs.videoPlayer.duration)) {
          this.duration = this.$refs.videoPlayer.duration
        }

        this.currentTime = this.$refs.videoPlayer.currentTime

        if (this.$refs?.videoPlayer.paused) {
          this.isPlaying = false
          this.$refs.videoPlayer.pause()
        } else {
          this.isPlaying = true
          this.$refs.videoPlayer.play()
        }

        // this.$emit('player-ready')
      }
    },
    formatTime (num) {
      let hours = Math.floor(num / 3600)
      let minutes = Math.floor((num % 3600) / 60)
      let seconds = Math.floor(num % 60)

      hours = hours < 10 ? "0" + hours : hours
      minutes = minutes < 10 ? "0" + minutes : minutes
      seconds = seconds < 10 ? "0" + seconds : seconds

      if (hours > 0) {
        return hours + ":" + minutes + ":" + seconds;
      }
      return minutes + ":" + seconds;
    },
    handleProgressClick (event) {
      const currentTime = (this.duration * event.offsetX) / this.$refs.videoPlayerProgress.offsetWidth
      this.currentTime = currentTime
      this.$refs.videoPlayer.currentTime = currentTime

      this.$emit('progress', currentTime)
    },
    handleTrackOnDrag (event) {
      if (event.x !== 0 && event.y !== 0) {
        const track = this.$refs.videoPlayerProgress

        if (track) {
          const leftMovement = event.pageX - track.getBoundingClientRect().left
          let drag = 0

          drag = leftMovement
          
          if (leftMovement < 0) {
            drag = 0
          } else if (leftMovement > track.offsetWidth) {
            drag = track.offsetWidth
          }

          this.currentTime = this.duration * (drag / track.offsetWidth)
          this.$refs.videoPlayer.currentTime = this.currentTime

          this.$emit('dragged', this.currentTime)
        }
      }
    },
    handleVideoPlaybackRate (speed) {
      this.speed = `${speed}x`
      this.$refs.videoPlayer.playbackRate = speed
      if (this.speedOpen) {
        this.speedOpen = false
      }
    },
    handleShowFunctions () {
      this.showFunctions = true
      this.showProgressBar = true
    },
    setTimeoutFunction () {
      const self = this

      setTimeout(() => {
        self.showFunctions = false
        self.speedOpen = false
        self.volumeOptionsOpen = false
      }, 6000)

      setTimeout(() => {
        self.showProgressBar = false
      }, 10000)
    }
  }
}
</script>

<style>
:root {
  --primary-color: #41b883;
  --control-background-color: rgba(45, 45, 45, 0.867);
  --top-options: -145px;
}

.video__container {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  cursor: pointer;
  background: #000;
  /* min-width: 600px; */
  /* min-height: 340px; */
  margin: 0 auto;
}

.video__player {
  /* border-radius: 6px; */
  width: 100%;
  height: 100%;
  touch-action: manipulation;
}

.spinner {
  z-index: 2;
  position: absolute;
}

.video__player source {
  height: 100%;
}

.video__controls {
  position: absolute;
  bottom: 10px;
  background: var(--control-background-color);
  padding: 15px;
  z-index: 2;
  width: 100%;
  align-items: center;
  color: #fff;
  border-radius: 6px;
}

.video__controls__progress__container {
  display: flex;
  width: 100%;
}

.video__controls__functions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%;
}

.video__controls__functions>div {
  display: flex;
}

.video__controls__functions .video__controls__configs {
  display: flex;
  justify-self: flex-end;
}

.video__controls__volume {
  position: relative;
}

.video__controls__volume--options {
  position: absolute;
  height: 100px;
  padding: 5px 8px;
  left: 5px;
  top: var(--top-options);
  background: var(--control-background-color);
  border-radius: 0.25rem;
}

.video__controls__volume--track {
  position: relative;
  height: 100%;
  width: 4px;
  border-radius: 6px;
  background-color: #8c8c8c;
}

.video__controls__volume--track-current {
  background-color: var(--primary-color);
  position: absolute;
  bottom: 0;
  left: 0;
  width: 4px;
}

.video__controls__volume--track-ball {
  width: 20px;
  height: 0.9375rem;
  border-radius: 13px;
  position: absolute;
  background-color: #fff;
  border: 0.125rem solid #222;
  left: -7px;
}

.video__controls__duration {
  justify-self: flex-end;
  margin: 3px;
}

.video__controls__duration span {
  margin: 0 3px;
}

.video__controls__progress {
  width: 100%;
  flex: 1;
  display: flex;
  align-items: center;
  margin: 0 0.45rem;
  background: #000;
  height: 0.25rem;
  position: relative;
}

.video__controls__progress__track {
  background: var(--primary-color);
  transition: width 0.2ms;
  display: flex;
  height: 0.25rem;
  border-radius: 6px;
}

.video__controls__progress__track--watching {
  height: 1.3rem;
  width: 0.5rem;
  border-radius: 20px;
  background: #fff;
  border: 1px solid #000;
  position: absolute;
  left: 0;
  bottom: -0.5rem;
}

.video__controls__speed {
  position: relative;
  min-width: 60px;
  padding: 0px 15px;
  top: 0;
}

.video__controls__speed__options {
  position: absolute;
  left: 0;
  top: -220px;
  background: var(--control-background-color);
  border-radius: 0.25rem;
}

.video__controls__speed__options .active {
  background: rgba(255, 255, 255, 0.2);
}

.video__controls__speed__options div {
  padding: 5px;
}

.video__controls__speed__options div:hover {
  background: rgba(255, 255, 255, 0.35);
  padding: 5px;
  color: #000;
}
</style>
