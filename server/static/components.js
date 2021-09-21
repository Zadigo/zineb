var something = Vue.extend({})

var navigationDrawer = {
    template: `
    <v-navigation-drawer permanent>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-h6">
            Application
          </v-list-item-title>
          <v-list-item-subtitle>
            subtext
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item v-for="item in items" :key="item.title" link>
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>
                {{ item.title }}
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    `,
    data () {
        return {
            items: [
                { title: 'Dashboard', icon: 'mdi-view-dashboard' },
                { title: 'Photos', icon: 'mdi-image' },
                { title: 'About', icon: 'mdi-help-box' },
            ],
            right: null,
        }
    }
}

var baseLayout = {
    name: 'BaseLayout',
    template: `
    <v-row class="mt-5">
        <v-col cols="12">
            <v-card>
                <v-card-title>
                    Spiders / {{ pageTitle }}
                </v-card-title>                
            </v-card>   
        </v-col>

        <v-row>
            <v-col cols="8">
                <router-view name="left" />    
            </v-col>
                
            <v-col cols="4">
                <router-view name="right" />    
            </v-col>
        </v-row>
    </v-row>
    `,
    computed: {
        pageTitle () {
            return this.$route.name
        }
    }
}

var spidersPage = {
    name: 'SpidersPage',
    template: `
    <v-row>
        <v-col cols="12">
            <v-card>
                <v-toolbar>
                    <v-toolbar-title>Zineb</v-toolbar-title>

                    <v-spacer></v-spacer>
                    
                    <v-menu>
                        <template v-slot:activator="{ on , attrs}">
                            <v-btn v-on="on" v-bind="attrs" icon>
                                <v-icon>mdi-dots-vertical</v-icon>
                            </v-btn>
                        </template>

                        <v-list>
                            <v-list-item :to="{ name: 'create' }" link>
                                <v-list-item-title>
                                    <v-icon class="mr-2">mdi-pen</v-icon>Create
                                </v-list-item-title>
                            </v-list-item>
                            
                            <v-list-item link>
                                <v-list-item-title>
                                    <v-icon class="mr-2">mdi-delete</v-icon>Delete
                                </v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                </v-toolbar>

                <v-card-text>
                    <v-data-table :headers="headers" :items="getSpiders"></v-data-table>

                    <template v-slot:header.name="{ header }">
                        {{ header.text.toUpperCase() }}
                    </template>
                </v-card-text>
            </v-card>
        </v-col>
    </v-row>
    `,
    data () {
        return {
            headers: [
                {
                    text: 'Name',
                    value: 'name'
                },
                {
                    text: 'Last execution',
                    value: 'last_execution'
                }
            ]
        }
    },
    beforeRouteEnter (to, from, next) {
        next(vm => {
            vm.$api.settings.get()
            .then((response) => {
                vm.$store.commit('setSettings', response.data)
            })
            .catch((error) => {
                console.error(error)
            })
        })
    },
    computed: {
        ...Vuex.mapGetters([
            'getSpiders'
        ])
    }
}

var createPage = {
    name: 'CreatePage',
    template: `
    <v-card>
        <v-card-text>
            <label>Spider name</label>
            <v-text-field v-model="spiderDetails.name" :min="1" :max="10" solo></v-text-field>
            
            <label>Spider type</label>
            <v-combobox v-model="spiderDetails.spiderType" :items="spiderTypes"></v-combobox>
        </v-card-text>

        <v-card-actions>
            <v-btn @click="createSpider" text>Create</v-btn>
        </v-card-actions>
    </v-card>
    `,
    data () {
        return {
            name: null,
            spiderTypes: ['HTTP', 'Files'],

            spiderDetails: {
                name: null,
                spiderType: null
            }
        }
    },
    methods: {
        createSpider () {
            this.$api.spiders.create(this.spiderDetails)
            .then((response) => {
                this.$store.commit('updateSettings', response.data)
                this.$router.push({ name: 'home' })
            })
            .catch((error) => {
                console.error(error)
            })
        }
    }
}

var settingsPage = {
    
}
