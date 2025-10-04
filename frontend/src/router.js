import {createRouter, createWebHashHistory} from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('./components/Home.vue'),
    },
    {
        path: '/:path*',
        name: 'Archive',
        component: () => import('./components/Archive.vue'),
        props: true
    },
    {
        path: '/search',
        name: 'Search',
        component: () => import('./components/Search.vue'),
        alias: '/search.html',
    },
    {
        path: '/tags',
        name: 'Tags',
        component: () => import('./components/Tags.vue'),
    },
    {
        path: '/files',
        name: 'Files',
        component: () => import('./components/FileBrowser.vue'),
    },
    {
        path: '/about',
        name: 'About',
        component: () => import('./components/About.vue'),
    },
    {
        path: '/takeout',
        name: 'Data Takeout',
        component: () => import('./components/Takeout.vue'),
    },
    {
        path: '/definition',
        name: 'Definition',
        component: () => import('./components/Definition.vue'),
    },
    {
        path: '/ultra-random',
        name: 'Ultra Random',
        component: () => import('./components/UltraRandom.vue'),
    }
    // {
    //     path: '/card-ideas',
    //     name: 'Card Ideas',
    //     component: () => import('./components/CardIdeas.vue'),
    // }
]


const router = createRouter({
    history: createWebHashHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    // hack to allow for forward slashes in path ids
    if (to.fullPath.includes('%2F')) {
        next(to.fullPath.replace(/%2F/g, '/'));
    } else {
        next();
    }
});

export default router
