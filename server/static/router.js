const routes = [
    {
        path: '/',
        component: BaseLayout,
        children: [
            {
                name: 'home',
                path: '',
                components: {
                    default: SpidersView
                }
            },
            {
                name: 'spider',
                path: 'spider/:id(\d+)',
                components: {
                    default: SpiderView
                }
            },
            {
                name: 'settings',
                path: 'settings',
                components: {
                    default: SettingsView
                }
            }
        ]

    }
]

var router = VueRouter.createRouter({
    history: VueRouter.createWebHistory(),
    routes
})


//     {
            //         name: 'create',
            //         path: 'create',
            //         components: {
            //             left: createPage,
            //             right: null
            //         }
            //     }
            // ]
            // components: {
            //     default: indexPage
            // },
            // beforeRouteEnter (to, from, next) {

            // }
