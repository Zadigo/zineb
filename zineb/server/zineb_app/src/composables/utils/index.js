import _ from 'lodash'
import { ref, watchEffect } from 'vue'

function raiseError (functionName, message) {
  throw new Error(`${functionName} - ${message}`)
}

export function loadView (name) {
  return () => import(`@/views/${name}.vue`)
}

export function loadLayout (name) {
  return () => import(`@/layouts/${name}.vue`)
}

export function loadComponent (name) {
  return () => import(`@/components/${name}.vue`)
}

export function scrollToTop () {
  window.scroll(0, 0)
}

export function asyncTimeout (ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export function useUtilities () {
  function getRandomString (k = 10) {
    let result = ''
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    const charactersLength = characters.length
    for (let i = 0; i < k; i++) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength))
    }
    return result
  }

  function hasNull (items) {
    let itemsValues = []

    if (typeof items === 'object') {
      itemsValues = Object.values(items)
    }

    return _.some(itemsValues, (item) => {
      return item === null || item === ""
    })
  }

  function indexElements (items) {
    items.forEach((item) => {
      if (!(typeof item === 'object')) {
        raiseError('indexElements', `${item} is not a dictionnary`)
        return null
      } else {
        item.id = 1
        return item
      }
    })
  }

  function incrementLastId (items) {
    if (!items) {
      return 1
    } else {
      if (items.length === 0) {
        return 1
      }

      const lastItem = _.last(items)

      if (!(typeof lastItem === 'object')) {
        raiseError('incrementLastId', `${lastItem} is not a dictionnary`)
        return null
      } else {
        return lastItem.id + 1
      }
    }
  }

  function readFile (file) {
    var filePreview = null

    if (file && file[0]) {
      const reader = new FileReader

      reader.onload = e => {
        filePreview = e.target.result
      }

      reader.readAsDataURL(file[0])
    }
    return filePreview
  }

  function readMultipleFiles (files) {
    return Object.entries(files).map((file) => {
      return readFile({ [`${file[0]}`]: file[1] })
    })
  }

  function readVideoFile (files) {
    return URL.createObjectURL(files[0])
  }

  function getVideoFrame (video) {
    const canvas = document.createElement('canvas')
    canvas.height = video.videoHeight
    canvas.width = video.videoWidth

    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    const img = new Image()
    const url = canvas.toDataURL()
    img.src = url
    img.classList.add('img-fluid')
    return [img, url]
  }

  function truncate (text, k = 28) {
    if (!(typeof text === 'string')) {
      raiseError('truncate', `${text} should be a string`)
      return ''
    } else {
      return `${text.slice(0, k)}...`
    }
  }

  function conditionalTruncate (text, limit, k) {
    if (text.length >= limit) {
      return truncate(text, k)
    } else {
      return text
    }
  }

  function listManager (items, item) {
    if (items.includes(item)) {
      const index = _.indexOf(items, item)
      items.splice(index, 1)
    } else {
      items.push(item)
    }
    return items
  }

  function dictionnaryListManager (items, item, key) {
    const result = _.filter(items, [key, item[key]])
    if (result.length > 0) {
      const index = _.findIndex(items, [key, item[key]])
      items.splice(index, 1)
    } else {
      items.push(item)
    }
    return items
  }

  function dictionnaryExists (items, key, test) {
    const result = _.filter(items, (item) => {
      const keyValue = item[key]
      return keyValue === test
    })
    return result.length > 0
  }

  function increaseIndex (items, initialIndex) {
    var newIndex = initialIndex + 1

    if (newIndex > items.length - 1) {
      newIndex = 0
    }
    return newIndex
  }

  function decreaseIndex (items, initialIndex) {
    var newIndex = initialIndex - 1

    if (newIndex < 0) {
      newIndex = items.length - 1
    }
    return newIndex
  }

  function scrollToSection (elementId) {
    document.getElementById(elementId).scrollIntoView()
  }

  function capitalizeFirstLetter (value) {
    if (!value) {
      return value
    }
    return value.charAt(0).toUpperCase() + value.slice(1)
  }

  function capitalizeLetters (value) {
    var tokens = value.split(" ")
    var result = tokens.map((token) => {
      return capitalizeFirstLetter(token)
    })

    return result.join(" ")
  }

  function formatAsPercentage (value, negative = false) {
    return negative ? `-${value}%` : `${value}%`
  }

  function getVerticalScrollPercentage (el) {
    var parent = el.parentNode
    return (el.scrollTop || parent.scrollTop) / (parent.scrollHeight - parent.clientHeight) * 100
  }

  function quickSort (items, ascending = true) {
    return items.sort((a, b) => {
      return ascending ? a - b : b - a
    })
  }

  return {
    capitalizeFirstLetter,
    capitalizeLetters,
    conditionalTruncate,
    decreaseIndex,
    dictionnaryExists,
    dictionnaryListManager,
    formatAsPercentage,
    getRandomString,
    getVerticalScrollPercentage,
    getVideoFrame,
    hasNull,
    indexElements,
    incrementLastId,
    increaseIndex,
    listManager,
    loadComponent,
    loadLayout,
    loadView,
    quickSort,
    readFile,
    readMultipleFiles,
    readVideoFile,
    scrollToSection,
    truncate
  }
}

export function useSocket () {
  const socket = ref(null)

  watchEffect(() => {
    if (socket.value === null) {
      return false
    } else {
      const result = socket.value === socket.value.OPEN
      console.log(result)
      return true
    }
  }, {
    onTrigger (e) {
      console.log('watchEffect', e)
    }
  })

  function getWebsocketProtocole () {
    var protocol = window.location.protocol
    return protocol === 'https' ? 'wss://' : 'ws://'
  }

  function websocketRootAddress (path) {
    var protocol = getWebsocketProtocole()
    var host = process.env.HOST_ADDRESS || '127.0.0.1:8000'
    return new URL(path, protocol + host).toString()
  }

  function createWebsocket (path, listeners = {}) {
    // const socket = new WebSocket(websocketRootAddress(path))

    // socket.onopen = listeners.onopen
    // socket.onclose = listeners.onclose
    // socket.onmessage = listeners.onmessage
    // socket.onerror = listeners.onerror

    // return socket

    const instance = new WebSocket(websocketRootAddress(path))
    socket.value = instance
    socket.value.onopen = listeners.onopen
    socket.value.onclose = listeners.onclose
    socket.value.onmessage = listeners.onmessage
    socket.value.onerror = listeners.onerror
  }

  function send (type, items = {}) {
    return JSON.stringify({ type: type, ...items })
  }

  return {
    socket,
    getWebsocketProtocole,
    websocketRootAddress,
    createWebsocket,
    send
  }
}

export function useUrls () {
  function rebuildPath (path) {
    var instance = new URL(path, window.location.href)
    return instance.toString()
  }

  function mediaUrl (path) {
    var rootUrl = process.env.rootUrl || 'http://127.0.0.1:8000'
    return new URL(path, rootUrl).toString()
  }

  function buildLimitOffset (url, limit = 100, offset = 0) {
    let defaultLimit = 100
    let defaultOffset = 0

    if (url) {
      const instance = new URL(url)
      const potentialLimit = instance.searchParams.get('limit')
      const potentialOffset = instance.searchParams.get('offset')

      defaultLimit = potentialLimit || limit
      defaultOffset = potentialOffset || offset
    }

    return new URLSearchParams({ limit: defaultLimit, offset: defaultOffset })
  }

  function getPageFromParams (url, page = 1) {
    let defaultPage = 1

    if (url) {
      const instance = new URL(url)
      const potentialPage = instance.searchParams.get('page')
      defaultPage = potentialPage || page
    }
    return new URLSearchParams({ page: defaultPage })
  }

  return {
    buildLimitOffset,
    getPageFromParams,
    mediaUrl,
    rebuildPath
  }
}
