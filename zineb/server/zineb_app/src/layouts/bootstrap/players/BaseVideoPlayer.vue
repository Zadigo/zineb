<template>
  <!-- @click="playPause" -->
  <div ref="videoContainer" class="video-container">
    <!-- Spinner -->
    <div v-if="isLoading" class="load-wrapp opacity-50">
      <div class="load-2">
        <span class="visually-hidden">Loading 2</span>
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
      </div>
    </div>

    <!-- Player -->
    <!-- @progress="percentageLoaded" -->
    <!-- @mousedown.right="handleInteractiveMenu" -->
    <!-- <video ref="videoPlayer" class="video-player" preload="metadata" controlist="nodownload" oncontextmenu="return false;" @seeked="$emit('loaded-meta-data', $refs.videoPlayer)" @loadmetadata="getVideoDetails" @timeupdate="getVideoDetails" @waiting="isLoading = true" @canplay="isLoading = false"> -->
    <video ref="videoPlayer" class="video-player" preload="metadata" controlist="nodownload" oncontextmenu="return false;" @loadedmetadata="getVideoDetails" @timeupdate="getVideoDetails" @waiting="isLoading=true" @canplay="isLoading=false" @click.stop="playPause">
      <source :src="videoSource" type="video/mp4">
      <!-- <track :src="require('assets/subtitles-en.vtt')" kind="subtitles" label="English" srclang="en" default> -->
    </video>

    <!-- Video Controls -->
    <!-- v-if="showControls && hideControls" -->
    <div class="video-controls">
      <!-- Track progress -->
      <div class="video-control-progress-container">
        <div ref="videoProgress" class="track" @click.stop.prevent="progressClick($event)">
          <div :style="{ width: `${progress}%` }" class="track-low"></div>
          <div class="track-selection"></div>
        </div>

        <div :style="{ left: `${progress}%` }" class="handle"></div>
      </div>

      <div>
        <transition name="opacity">
          <div v-if="showVideoSettings" class="p-1 bg-dark" style="position: absolute; left: calc(100% - 300px); bottom: 100%;height: auto;width: 300px;margin-bottom: .5rem;border-radius: .5rem;" @mouseleave="showVideoSettings=false">
            <div class="row p-1 mb-3">
              <div class="col-6 justify-content-start">
                <button v-if="showSpeedSettings || showQualitySettings" type="button" class="btn btn-light btn-sm" @click="showSpeedSettings = false, showQualitySettings = false">
                  <font-awesome-icon icon="fa-solid fa-arrow-left" />
                </button>
              </div>

              <div class="col-6 d-flex justify-content-end" @click="showVideoSettings=false">
                <button type="button" class="btn btn-light btn-sm">
                  <font-awesome-icon icon="fa-solid fa-close" />
                </button>
              </div>
            </div>

            <div v-if="!showSpeedSettings && !showQualitySettings" :key="0" class="list-group">
              <a href class="list-group-item list-group-item-action d-flex justify-content-between align-items-center bg-transparent text-light border-0" @click.prevent="showSpeedSettings = true">
                <span>
                  <font-awesome-icon icon="fa-solid fa-gauge-simple" class="me-2" /> Playback speed
                </span>
                <span>{{ speed }}
                  <font-awesome-icon icon="fa-solid fa-arrow-right" class="ms-2" />
                </span>
              </a>

              <a href class="list-group-item list-group-item-action d-flex justify-content-between align-items-center bg-transparent text-light border-0" @click.prevent="showQualitySettings = true">
                <span>
                  <font-awesome-icon icon="fa-solid fa-star" class="me-2" /> Quality
                </span>
                <span>{{ quality }}
                  <font-awesome-icon icon="fa-solid fa-arrow-right" class="ms-2" />
                </span>
              </a>
            </div>

            <div v-if="showSpeedSettings" :key="1" class="list-group">
              <a v-for="speed in speeds" :key="speed" href class="list-group-item list-group-item-action bg-transparent text-light" @click.prevent="playbackSpeedClick(speed)">
                {{ `${speed}x` }}
              </a>
            </div>

            <div v-if="showQualitySettings" :key="3" class="list-group">
              <a href type="button" class="list-group-item list-group-item-action bg-transparent text-light" @click.prevent>1080p</a>
              <a href type="button" class="list-group-item list-group-item-action bg-transparent text-light" @click.prevent>720p</a>
              <a href type="button" class="list-group-item list-group-item-action bg-transparent text-light" @click.prevent>480p</a>
            </div>
          </div>
        </transition>

        <!-- Volume -->
        <transition name="opacity">
          <div v-if="showVolume" class="video-control-volume-container" @mouseleave="showVolume=false">
            <div ref="volumeControl" class="track" @click="volumeClick">
              <div :style="{ width: `${volume * 100}%` }" class="track-low"></div>
              <!-- <div class="handle"></div> -->
            </div>
          </div>
        </transition>

        <!-- Actions -->
        <div class="video-control-actions">
          <!-- Left -->
          <div class="d-flex justify-content-left align-items-center gap-3">
            <button type="button" class="btn btn-light shadow-none" @click.stop="playPause">
              <font-awesome-icon v-if="!isPlaying" icon="fa-solid fa-play" />
              <font-awesome-icon v-else icon="fa-solid fa-pause" />
            </button>

            <div class="video-control-duration mx-3">
              <span>{{ currentTimeFormatted }}</span>
              <span>{{ durationFormatted }}</span>
            </div>
          </div>

          <!-- Right -->
          <div class="video-control-configuration-center d-flex justify-content-end">
            <div class="video-control-settings">
              <button type="button" class="btn btn-light" @click="showVideoSettings=!showVideoSettings">
                <font-awesome-icon icon="fa-solid fa-cog" />
              </button>
            </div>

            <div class="video-control-volume ms-2">
              <button type="button" class="btn btn-light" @click="showVolume=!showVolume">
                <font-awesome-icon v-if="volume < 0.1" icon="fa-solid fa-volume-low" />
                <font-awesome-icon v-else-if="volume >= 0.1 && volume <= 0.8" icon="fa-solid fa-volume-up" />
                <font-awesome-icon v-else-if="volume > 0.8" icon="fa-solid fa-volume-high" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Interactive menu -->
    <!-- <div ref="interactiveMenu" class="interactive-menu" @mouseleave="showInteractiveMenu=false">
      <ul class="list-unstyled">
        <li>Copy video url</li>
        <li>Copy video url at current time</li>
      </ul>
    </div> -->
  </div>
</template>

<script>
// import { onKeyStroke } from '@vueuse/core'

export default {
  name: 'BaseVideoPlayer',
  props: {
    captureFrames: {
      type: Boolean
    },
    // hideControls: {
    //   type: Boolean
    // },
    revokeUrl: {
      type: Boolean
    },
    videoUrl: {
      type: String,
      required: true,
    }
  },
  emits: {
    play() {
      return true
    },
    pause () {
      return true
    },
    'update:time'() {
      return true
    },
    'loaded-meta-data' () {
      return true
    },
    'update:volume' () {
      return true
    },
    'update:frames' () {
      return true
    }
  },
  data () {
    return {
      videoSource: null,
      isPlaying: false,
      isLoading: true,
      duration: 0,
      currentTime: 0,
      speed: '1x',
      quality: '1080p',
      volume: 0.5,
      speeds: [2, 1.75, 1.5, 1, 0.75, 0.5],

      showVideoSettings: false,
      showSpeedSettings: false,
      showQualitySettings: false,
      showVolume: false,
      showInteractiveMenu: false,
      showControls: false
    }
  },
  computed: {
    currentTimeFormatted () {
      return this.formatTime(this.currentTime)
    },
    durationFormatted () {
      return this.formatTime(this.duration)
    },
    progress () {
      // Indicates the % of tthe video that was read
      return (this.currentTime / this.duration) * 100
    }
  },
  watch: {
    currentTime (current) {
      if (current === this.duration) {
        // TODO: Run an event or a callback
        // when the video is terminated
        console.info('terminated')
      }
    },
    videoUrl (current, previous) {
      if (current !== previous) {
        // NOTE: We have to manually set the source
        // on the video since once mounted, Vue does not
        // automatically remount the source tag
        // console.log('video player watch', current, previous)
        this.videoSource = this.videoUrl
        this.$refs.videoPlayer.src = this.videoSource
        this.getVideoDetails()
      }
    }
  },
  mounted () {
    this.videoSource = this.videoUrl
    // this.getVideoDetails()

    // const self = this
    // onKeyStroke(['p', ' ', 'k'], function (e) {
    //   e.preventDefault()
    //   self.playPause()
    // })
    // onKeyStroke('ArrowUp', function (e) {
    //   e.preventDefault()
    //   let volume = self.volume += 0.1
    //   if (volume >= 1) {
    //     volume = 1
    //   }
    //   self.volume = volume
    //   self.$refs.videoPlayer.volume = volume
    // })
    // onKeyStroke('ArrowDown', function (e) {
    //   e.preventDefault()
    //   let volume = self.volume -= 0.1
    //   if (volume <= 0) {
    //     volume = 0
    //   }
    //   self.volume = volume
    //   self.$refs.videoPlayer.volume = volume
    // })
    // onKeyStroke(['ArrowLeft', 'j'], function (e) {
    //   e.preventDefault()
    // })
    // onKeyStroke(['ArrowRight', 'l'], function (e) {
    //   e.preventDefault()
    // })

    this.$emit('loaded-meta-data', this.$refs.videoPlayer)
  },
  beforeUnmount () {
    if (this.revokeUrl) {
      const source = this.$refs.videoPlayer.querySelector('source')
      URL.revokeObjectURL(source.src)
    }
  },
  methods: {
    playPause () {
      if (this.$refs?.videoPlayer.paused) {
        this.isPlaying = true
        this.$refs.videoPlayer.play()
        this.$emit('play')
      } else {
        this.isPlaying = true
        this.$refs.videoPlayer.pause()
        this.$emit('pause', [this.progress, this.formatTime(this.currentTime)])
      }
    },
    progressClick (event) {
      const currentTime = (this.duration * event.offsetX) / this.$refs.videoProgress.offsetWidth
      this.currentTime = currentTime
      this.$refs.videoPlayer.currentTime = currentTime
      this.$emit('update:time', currentTime)
    },
    volumeClick (event) {
      // Handle volume change
      const volumeControl = this.$refs.volumeControl
      const mousePosition = event.pageX
      const result = mousePosition - volumeControl.getBoundingClientRect().left
      const trackWidth = volumeControl.offsetWidth
      let value = result / trackWidth * 100
      value = Math.round(value / 1) * 1
      const currentVolume = Math.max(0, Math.min(100, value))
      this.volume = Math.round((currentVolume / 100) * 10) / 10
      this.$emit('update:volume', this.volume)
    },
    percentageLoaded (event) {
      // TODO: Handle how much of the video was loaded
      // when the user has seeked on not seeked
      // the video
      // see: https://developer.mozilla.org/en-US/docs/Web/Guide/Audio_and_video_delivery/buffering_seeking_time_ranges
      // see: https://stackoverflow.com/questions/5029519/html5-video-percentage-loaded
      if (this.$refs?.videoPlayer) {
        const percentageLoaded = event.target.buffered.length / this.duration
        console.log(percentageLoaded)
      }
    },
    playbackSpeedClick (speed) {
      // Handle video speed reading change
      this.speed = `${speed}x`
      this.$refs.videoPlayer.playbackRate = speed
      this.showSpeedSettings = false
    },
    handleInteractiveMenu (event) {
      // TODO: Allows an interative menu on the video
      const mousePositionX = event.clientX
      const mousePositionY = event.clientY
      // const containerWidth = this.$refs.videoContainer.offsetWidth
      // const containerHeight = this.$refs.videoContainer.offsetHeight
      // console.log(mousePositionX, mousePositionY, containerHeight, containerWidth)
      this.showInteractiveMenu = !this.showInteractiveMenu
      // const resultX = containerWidth - mousePositionX
      // const resultY = containerWidth - mousePositionY
      this.$refs.interactiveMenu.style.left = `${mousePositionX}px`
      this.$refs.interactiveMenu.style.top = `${mousePositionY}px`
    },
    getFrames () {
      // Get a couple of frames from 
      // the video for various purposes
      if (this.captureFrames) {
        const player = this.$refs.videoPlayer
        const canvas = document.createElement('canvas')
        canvas.height = player.videoHeight
        canvas.width = player.videoWidth

        const ctx = canvas.getContext('2d')
        ctx.drawImage(player, 0, 0, canvas.width, canvas.height)

        const img = new Image()
        const url = canvas.toDataURL()
        img.src = url
        img.classList.add('img-fluid')
        this.$emit('update:frames', [img, url])
      }
    },
    getVideoDetails () {
      // Get the main data for the video
      if (this.$refs?.videoPlayer) {
        const player = this.$refs.videoPlayer

        if (!Number.isNaN(player.duration)) {
          this.duration = player.duration
        }

        this.currentTime = player.currentTime

        // TODO: If we have an initial time,
        // place the player on the current
        // that initial time -: Use the #t=time
        // on the src link directly
        // see: https://blog.addpipe.com/10-advanced-features-in-html5-video-player/#startorstopthevideoatacertainpointortimestamp
        // player.currentTime = 3

        if (player.paused) {
          this.isPlaying = false
          player.pause()
        } else {
          this.isPlaying = true
          player.play()
        }

        this.getFrames()
      }
    },
    formatTime (value) {
      let hours = Math.floor(value / 3600)
      let minutes = Math.floor((value % 3600) / 60)
      let seconds = Math.floor(value % 60)

      hours = hours < 10 ? '0' + hours : hours
      minutes = minutes < 10 ? '0' + minutes : minutes
      seconds = seconds < 10 ? '0' + seconds : seconds

      if (hours > 0) {
        return `${hours}:${minutes}:${seconds}`
      }

      return `${minutes}:${seconds}`
    }
  }
}
</script>

<style scoped>
.video-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: rgba(38, 38, 38, 1);
  margin: 0 auto;
}

.video-player {
  width: 100%;
  height: 100%;
  touch-action: manipulation;
  z-index: 40;
}

.video-player source {
  height: 100%;
}

.video-controls {
  position: absolute;
  bottom: 5%;
  background: rgba(38, 38, 38, .8);
  padding: 1rem;
  width: 80%;
  align-items: center;
  color: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 4px 10px 0 rgb(0 0 0 / 20%), 0 4px 20px 0 rgb(0 0 0 / 10%);
  z-index: 50;
}

.video-control-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%;
}

.video-control-configuration .video-control-volume {
  position: relative;
}

@media (max-width: 576px) {
  .video-control-duration {
    display: none;
  }
}

.video-control-duration span:first-child::after {
  content: ":";
  margin: 0 3px;
}

.video-control-speed {
  position: relative;
  top: 0;
}

.video-control-speed .picker {
  position: absolute;
  right: 100%;
  bottom: -250%;
  background-color: rgba(38, 38, 38, 1);
  padding: .5rem;
  border-radius: 0.5rem;
}

.video-control-progress-container {
  position: relative;
  display: inline-block;
  vertical-align: middle;
  width: 100% !important;
  height: 20px;
  margin-bottom: 1rem;
}

.video-control-progress-container .track {
  position: absolute;
  cursor: pointer;
  background-color: white;
  background-repeat: repeat-x;
  box-shadow: inset 0 1px 2px rgb(0 0 0 / 10%);
  border-radius: 4px;
  height: 10px;
  width: 100%;
  margin-top: -5px;
  top: 50%;
  left: 0;
}

.video-control-progress-container .track-low {
  position: absolute;
  height: 100%;
  top: 0;
  bottom: 0;
  background: transparent;
  box-sizing: border-box;
  border-radius: 4px;
  background-color: #0d6efd;
  /* width: 50%; */
}

.video-control-progress-container .handle {
  position: absolute;
  background-color: #fff !important;
  background-repeat: repeat-x;
  /* box-shadow: 0 3px 1px -2px rgba(0, 0, 0, .2), 0 2px 2px 0 rgba(0, 0, 0, .14), 0 1px 5px 0 rgba(0, 0, 0, .12); */
  top: 0;
  width: 20px;
  height: 20px;
  filter: none;
  border: 0 solid transparent;
  border-radius: 50%;
  margin-left: -10px;
}

.video-control-configuration-center {
  position: relative;
}

.video-control-settings .picker {
  position: absolute;
  transition: height .5s ease;
  bottom: 80px;
  right: -30%;
  width: 300px;
  background: rgb(38, 38, 38);
  border-radius: .5rem;
  padding: .5rem;
  z-index: 100;
}

.video-control-volume-container {
  position: absolute;
  /* position: relative; */
  background-color: rgba(38, 38, 38, .8);
  display: inline-block;
  vertical-align: middle;
  width: 150px !important;
  height: 50px;
  margin-bottom: 1rem;
  border-radius: .5rem;
  bottom: 100%;
  left: calc(100% - 150px);
  display: inline-block;
  vertical-align: middle;
}

.video-control-volume-container .track {
  position: absolute;
  cursor: pointer;
  background-color: white;
  background-repeat: repeat-x;
  box-shadow: inset 0 1px 2px rgb(0 0 0 / 10%);
  border-radius: 4px;
  height: 5px;
  width: 100%;
  margin-top: -5px;
  top: 50%;
  left: 0;
}

.video-control-volume-container .track-low {
  position: absolute;
  height: 100%;
  top: 0;
  bottom: 0;
  background: transparent;
  box-sizing: border-box;
  border-radius: 4px;
  background-color: #0d6efd;
  width: 50%;
}

.video-control-volume-container .handle {
  position: absolute;
  background-color: #fff !important;
  background-repeat: repeat-x;
  top: 0;
  width: 15px;
  height: 15px;
  filter: none;
  border: 0 solid transparent;
  border-radius: 50%;
  /* margin-left: -10px; */
}

.load-wrapp {
  position: absolute;
  z-index: 3;
}

.opacity-enter-active,
.opacity-leave-active {
  transition: all .15s ease;
}

.opacity-enter-from,
.opacity-leave-to {
  opacity: 0;
  transform: translateX(50px);
}

.opacity-enter-to,
.opacity-leave-from {
  opacity: 1;
  transform: translateX(0px);
}

.interactive-menu {
  position: absolute;
  left: 10%;
  right: 0;
  z-index: 1000;
  background-color: rgba(38, 38, 38, .8);
  color: white;
  width: 300px;
  height: auto;
  border-radius: .25em;
}

.interactive-menu ul {
  margin: 0;
}

.interactive-menu li {
  padding: .5rem;
}

.interactive-menu li:first-child {
  border-top-right-radius: .25em;
  border-top-left-radius: .25em;
}

.interactive-menu li:last-child {
  border-bottom-right-radius: .25em;
  border-bottom-left-radius: .25em;
}

.interactive-menu li:hover {
  background-color: rgba(38, 38, 38, .3);
}
</style>
