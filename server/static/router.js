Vue.use(VueRouter)

var router = new VueRouter({
    mode: 'history',
    routes: [
        {
            path: '/',
            components: {
                default: baseLayout,
                nav: navigationDrawer
            },
            children: [
                {
                    name: 'home',
                    path: '',
                    components: {
                        left: spidersPage,
                        right: null
                    }
                },
                {
                    name: 'create',
                    path: 'create',
                    components: {
                        left: createPage,
                        right: null
                    }
                }
            ]
            // components: {
            //     default: indexPage
            // },
            // beforeRouteEnter (to, from, next) {

            // }
        }
    ]
})
