<template>
  <div class="container my-5">
    <div class="row">
      <div class="col-12 mb-2">
        <base-template-card>
          <template #default>
            <div class="card-body d-flex justify-content-left align-items-center">
              <base-button color="primary" @click="showCreationModal = true">Create</base-button>
              <base-button v-if="currentSpider === null" color="primary" class="mx-1" @click="currentSpider = null">Play all</base-button>
              <base-button v-else color="primary" class="mx-1" @click="currentSpider = null">Stop all</base-button>
              <base-button color="primary">Archive</base-button>
              <base-button color="danger" class="mx-1">Delete</base-button>
            </div>
          </template>
        </base-template-card>
      </div>
      
      <div class="col-8">
        <base-template-card>
          <template #default>
            <div class="card-header d-flex justify-content-between align-items-center">
              <base-input id="search" v-model="search" type="search" class="p-2 me-5 w-50" />
              <div class="actions">
                <base-button color="link">Filter</base-button>
                <base-button color="link" @click="showByGroup = !showByGroup">Group</base-button>
              </div>
            </div>
            
            <div class="card-body">
              <base-list-group v-if="showByGroup" v-slot="{ listGroupItems }" :items="groups">
                <div v-for="(item, i) in listGroupItems" :key="i" class="list-group-item list-group-item-action">
                  <div class="my-3">
                    <span class="badge text-bg-primary p-2 mb-4">{{ item }}</span>
                    <div v-for="(spider, y) in grouped[item]" :key="y" class="card">
                      <div class="card-body">
                        {{ spider.name }}
                      </div>
                    </div>
                  </div>
                </div>
              </base-list-group>

              <base-list-group v-else v-slot="{ listGroupItems }" :items="searchedSpiders">
                <div v-for="(item, i) in listGroupItems" :key="i" class="list-group-item list-group-item-action">
                  <div class="d-flex justify-content-between align-items-center">
                    <span>{{ item.name }} <span class="badgee ms-2">{{ item.label }}</span></span>
                    <base-button v-if="currentSpider === item.name" color="primary" size="sm" @click="currentSpider = null">Stop</base-button>
                    <base-button v-else color="primary" size="sm" @click="currentSpider = item.name">Run</base-button>
                  </div>

                  <base-template-card v-show="currentSpider === item.name" class="mt-2 shadow-none border">
                    <template #default>
                      <div class="card-body">
                        Running...
                      </div>
                    </template>
                  </base-template-card>
                </div>
              </base-list-group>

            </div>
          </template>
        </base-template-card>
      </div>
     
      <div class="col-4">
        <base-template-card>
          <template #default>
            <div class="card-body">
            </div>
          </template>
        </base-template-card>
      </div>
    </div>


    <base-offcanvas :show="showCreationModal" position="end" @close="showCreationModal = false">
      <template #default>
        <base-input id="name" v-model="options.name" type="search" class="p-2" />
        <base-input id="description" v-model="options.description" type="search" class="p-2 my-2" />

        <div class="offcanvas-footer">
          <base-button color="primary" @click="create">Create</base-button>
        </div>
      </template>
    </base-offcanvas>
  </div>
</template>

<script>
import { useSpiders } from '@/store/spiders'
import { storeToRefs } from 'pinia'
import _ from 'lodash'
import BaseInput from '@/layouts/bootstrap/BaseInput.vue'
import BaseTemplateCard from '@/layouts/bootstrap/cards/BaseTemplateCard.vue'
import BaseListGroup from '@/layouts/bootstrap/listgroup/BaseListGroup.vue'
import BaseButton from '@/layouts/bootstrap/buttons/BaseButton.vue'
import BaseOffcanvas from '@/layouts/bootstrap/BaseOffcanvas.vue'
export default {
  name: 'IndexView',
  components: {
    BaseTemplateCard,
    BaseListGroup,
    BaseButton,
    BaseInput,
    BaseOffcanvas
  },
  setup () {
    const store = useSpiders()
    const { spiders } = storeToRefs(store)
    return {
      spiders
    }
  }, 
  data () {
    return {
      currentSpider: null,
      showCreationModal: false,
      search: null,
      showByGroup: false,
      options: {
        name: null,
        description: null
      }
    }
  },
  computed: {
    searchedSpiders () {
      if (this.search === null || this.search === "") {
        return this.spiders
      } else {
        return _.filter(this.spiders, (spider) => {
          const truthArray = [
            spider.name === this.search,
            spider.name.includes(this.search),
            spider.name.toLowerCase() === this.search,
            spider.name.toLowerCase().includes(this.search)
          ]
          return _.some(truthArray, (value) => {
            return value === true
          })
        })
      }
    },
    groups () {
      return _.map(this.searchedSpiders, (spider) => {
        return spider.label
      })
    },
    grouped () {
      const groupTemplates = {}
      _.forEach(this.groups, (group) => {
        groupTemplates[group] = []
      })

      _.forEach(this.searchedSpiders, (spider) => {
        groupTemplates[spider.label].push(spider)
      })
      return groupTemplates
    }
  },
  methods: {
    async create () {
      this.showCreationModal = false
      // try {
      //   const response = await this.$http.post('/new', this.options)
      //   console.log(response)
      // } catch (e) {
      //   console.log(e)
      // }
    }
  }
}
</script>
