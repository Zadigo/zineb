<template>
  <div class="multiple-select">
    <!-- Search -->
    <div class="input-group mb-2">
      <input v-model="search" type="search" class="form-control">
      <base-button id="constraints" class="dropdown-toggle" outline @click="showConstraints = !showConstraints">
        {{ constraint }}
      </base-button>
      <dropdown-menu :show="showConstraints">
        <dropdown-item @click="constraint = 'Is'">Is</dropdown-item>
        <dropdown-item @click="constraint = 'Is not'">Is not</dropdown-item>
        <dropdown-item @click="constraint = 'Contains'">Contains</dropdown-item>
      </dropdown-menu>
    </div>

    <!-- Select -->
    <div class="wrapper">
      <div class="left rounded border">
        <transition-group name="select">
          <button v-for="item in unselectedItems" :key="item.id" type="button" class="btn btn-light shadow-none btn-block my-2" @click="handleSelection(item)">
            {{ item.text }}
          </button>
        </transition-group>
      </div>
  
      <div class="middle rounded">
        <button type="button" :class="{ disabled: unselectedItems.length === 0 }" class="btn btn-light btn-block shadow-none" @click="handleAddAll">A</button>
        <button type="button" :class="{ disabled: selectedItems.length === 0 }" class="btn btn-light btn-block shadow-none" @click="handleRemoveAll">R</button>
      </div>
      
      <div class="right rounded border">
        <transition-group name="select">
          <button v-for="item in selectedItems" :key="item.id" type="button" class="btn btn-light shadow-none btn-block my-2" @click="handleSelection(item)">
            {{ item.text }}
          </button>
        </transition-group>
      </div>
    </div>

    <!-- Hidden -->
    <input type="text" multiple>
  </div>
</template>

<script>
import _ from 'lodash'
import BaseButton from './buttons/BaseButton.vue'
import DropdownMenu from './buttons/DropdownMenu.vue'
import DropdownItem from './buttons/DropdownItem.vue'
export default {
  name: 'BaseMultipleSelect',
  components: {
    BaseButton,
    DropdownMenu,
    DropdownItem
  },
  props: {
    items: {
      type: Array,
      default: () => []
    },
    // initialUnselected: {
    //   type: Array,
    //   default: () => []
    // }
  },
  data () {
    return {
      search: null,
      selectedItemsId: [],
      showConstraints: false,
      constraint: 'Contains'
    }
  },
  computed: {
    searchedItems () {
      if (this.search === null || this.search === '') {
        return this.items
      } else {
        let result
        switch (this.constraint) {
          case 'Is':
            result = _.filter(this.items, (item) => {
              return (
                item.text === this.search ||
                item.text.toLowerCase() === this.search
              )
            })
            break
          
          case 'Is not':
            result = _.filter(this.items, (item) => {
              return (
                item.text !== this.search ||
                item.text.toLowerCase() !== this.search
              )
            })
            break

          case 'Contains':
            result = _.filter(this.items, (item) => {
              return (
                item.text.includes(this.search) ||
                item.text.toLowerCase().includes(this.search)
              )
            })
            break
        
          default:
            result = []
            break
        }
        return result
      }
    },
    unselectedItems () {
      if (this.selectedItemsId.length === 0) {
        return this.searchedItems
      }
      return _.filter(this.items, (item) => {
        return !this.selectedItemsId.includes(item.id)
      })
    }, 
    selectedItems () {
      return _.filter(this.items, (item) => {
        return this.selectedItemsId.includes(item.id)
      })
    }
  },
  methods: {
    selectItem (itemId) {
      if (this.selectedItemsId.includes(itemId)) {
        const index = _.indexOf(this.selectedItemsId, itemId)
        this.selectedItemsId.splice(index, 1)
      } else {
        this.selectedItemsId.push(itemId)
      }
    },
    handleSelection (item) {
      this.selectItem(item.id)
    },
    handleAddAll () {
      if (this.search === null || this.search === '') {
        this.selectedItemsId = _.map(this.items, (item) => {
          return item.id
        })
      } else {
        this.selectedItemsId = _.map(this.searchedItems, (item) => {
          return item.id
        })
        this.search = null
      }
    },
    handleRemoveAll () {
      this.selectedItemsId = []
    }
  }
}
</script>

<style scoped>
.multiple-select {
  width: 100%;
  height: auto;
  overflow: hidden;
}

.multiple-select .wrapper {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  align-items: center;
  gap: .5rem;
}

.multiple-select .wrapper .middle {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: .5rem;
  padding: 1rem;
  width: 10%;
  background-color: rgba(0, 0, 0, .075);
  height: 200px;
}

.multiple-select .wrapper .left,
.multiple-select .wrapper .right {
  padding: 1rem;
  overflow-y: scroll;
  min-height: 100px;
  height: 200px;
  width: 45%;
}

.multiple-select .wrapper .left::-webkit-scrollbar,
.multiple-select .wrapper .right::-webkit-scrollbar {
  display: none;
}

.select-enter-active,
.select-leave-active {
  transition: all .15s ease-in-out;
}

.select-enter-from,
.select-leave-to {
  transform: scale(0.9);
}

.select-enter-to,
.select-leave-from {
  transform: scale(1);
}

.select-move {
  transition: all .15s ease;
}
</style>
