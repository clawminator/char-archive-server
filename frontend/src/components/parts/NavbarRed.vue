<template>
  <nav class="nav-header">
    <div class="left-0 w-full z-10 absolute">
      <div class="flex flex-wrap items-center justify-between mt-0 md:ml-3 md:mr-3">
        <div class="flex items-center max-md:pl-4">
          <a class="no-hover" href="/#/">
            <logo-square-svg class="inline-block align-middle fill-current logo" style="height:42px"></logo-square-svg>
            <h3 class="no-underline hover:no-underline inline-block middle pl-1 prose text-2xl max-sm:hidden"
                style="margin-left: 10px;"> Character Archive</h3>
          </a>
        </div>

        <div class="pr-4">
          <button id="nav-toggle"
                  class="block md:hidden items-center px-3 py-2 border rounded text-grey border-grey-dark appearance-none focus:outline-none"
                  @click="toggleNav($event)">
            <svg class="fill-current h-3 w-3" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <title>Menu</title>
              <path d="M0 3h20v2H0V3zm0 6h20v2H0V9zm0 6h20v2H0v-2z"></path>
            </svg>
          </button>
        </div>

        <div
            v-show="navVisible"
            id="nav-content"
            class="w-full flex-grow md:flex md:flex-1 md:content-center md:justify-end md:mt-0 z-20 max-md:rounded-b-xl">
          <ul class="list-reset md:flex justify-end items-center">
            <li class="min-md:mr-3 py-2 md:py-0 max-md:text-xl">
              <h3 class="navbar-item w-full text-center middle">
                <router-link
                    :class="{ 'text-baby-blue': isActive }"
                    class="inline-block py-2 no-underline text-white"
                    tag="a"
                    to="/"
                    @click="matoPush('User Interface', 'Red Nav Click', 'Archive')">
                  Archive
                </router-link>
              </h3>
            </li>
            <li class="min-md:mr-3 py-2 md:py-0 max-md:text-xl">
              <h3 class="navbar-item w-full text-center middle">
                <router-link
                    active-class="text-baby-blue"
                    class="inline-block py-2 no-underline text-white"
                    tag="a"
                    to="/files"
                    @click="matoPush('User Interface', 'Red Nav Click', 'Files')">
                  Files
                </router-link>
              </h3>
            </li>
            <li class="min-md:mr-3 py-2 md:py-0 max-md:text-xl">
              <h3 class="navbar-item w-full text-center middle">
                <router-link
                    active-class="text-baby-blue"
                    class="inline-block py-2 no-underline text-white"
                    tag="a"
                    to="/takeout"
                    @click="matoPush('User Interface', 'Red Nav Click', 'Data Takeout')">
                  Takeout
                </router-link>
              </h3>
            </li>
            <li class="min-md:mr-3 py-2 md:py-0 max-md:text-xl">
              <h3 class="navbar-item w-full text-center middle">
                <router-link
                    active-class="text-baby-blue"
                    class="inline-block py-2 no-underline text-white"
                    tag="a"
                    to="/about"
                    @click="matoPush('User Interface', 'Red Nav Click', 'About')">
                  About
                </router-link>
              </h3>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import {matoPush} from "@/assets/js/mato";
import {mapState} from 'vuex';
import LogoSquareSvg from "@/components/svg/logo-svg.vue";
import router from "@/router";


export default {
  name: 'NavbarRed',
  components: {LogoSquareSvg},
  data() {
    return {
      navVisible: false,
    }
  },
  computed: {
    isActive() {
      return this.$route.path === '/' || this.$route.path === '/search'
    },
    ...mapState(["showFolderModal", "searchQuery", "siteDisabled"])
  },
  methods: {
    matoPush,
    forceNavOpen(event) {
      event.stopPropagation()
      this.navVisible = true
    },
    toggleNav(event) {
      this.navVisible = !this.navVisible
    },
    handleResize() {
      this.navVisible = window.innerWidth > 767
    },
  },
  mounted() {
    this.navVisible = window.innerWidth > 767
  },
  created() {
    window.addEventListener('resize', this.handleResize);
    this.handleResize()
    router.beforeEach((to, from, next) => {
      // Manually close the navbar.
      if (window.screen.width < 768) {
        this.navVisible = false
      }
      next()
    });
  },
}
</script>

<style scoped>
@import '@/assets/css/colors.css';
@import '@/assets/css/navbar-red.css';
</style>
