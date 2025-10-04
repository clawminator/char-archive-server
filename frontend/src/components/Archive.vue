<template>
  <NavbarRed/>
  <div :key="$route.fullPath" class="archive-container md:px-10 pt-5 mt-[60px]">
    <div v-if="!archiveIs404 && !archiveIs500 && !archiveIs429" class="w-full">
      <div v-if="Object.keys(cardData).length > 0" class="card w-full">
        <ArchiveItem/>
      </div>
      <Author v-else-if="Object.keys(authorData).length > 0"/>
      <div v-else class="w-full">
        <div class="flex flex-col items-center justify-center mb-5">
          <div class="loader my-10"></div>
        </div>
      </div>
    </div>
    <div v-else-if="archiveIs404" class="w-full">
      <div class="flex flex-col items-center justify-center mb-5">
        <h1 class="text-xl sm:text-xl md:text-4xl font-bold my-10 prose">404 Not Found</h1>
        <a href="/#/">Back Home</a>
      </div>
    </div>
    <div v-else-if="archiveIs500" class="w-full">
      <div class="flex flex-col items-center justify-center mb-5">
        <h1 class="text-xl sm:text-xl md:text-4xl font-bold my-10 prose">500 Internal Server Error</h1>
        <a href="/#/">Back Home</a>
      </div>
    </div>
    <div v-else-if="archiveIs429" class="w-full">
      <div class="flex flex-col items-center justify-center mb-5">
        <h1 class="text-xl sm:text-xl md:text-4xl font-bold my-10 prose">429 Too Many Requests</h1>
        <a href="/#/">Back Home</a>
      </div>
    </div>
  </div>
  <Alerts/>
</template>

<script>

// TODO: need to refer to chub cards by their author, name, AND id. Path should be something like /author/type/name/id
// TODO: why is this endpoint called twice? /api/archive/v1/chub/node/character/
// TODO: make sure to update the matomo url when calling: `_paq.push(['setCustomUrl', window.location.href])`

import NavbarRed from "@/components/parts/NavbarRed.vue";
import ArchiveHome from "@/components/parts/archive/ArchiveHome.vue";
import axios from "axios";
import {APIHOST} from "@/components/config";
import Alerts from "@/components/parts/Alerts.vue";
import 'highlight.js/styles/atom-one-dark.css';
import 'flowbite';
import {mapState} from "vuex";
import ArchiveItem from "@/components/parts/archive/Item.vue";
import Author from "@/components/parts/archive/Author.vue";
import SearchResults from "@/components/Search.vue";
import {initializeHandler} from "@/assets/js/source-handler/initialize";


export default {
  name: 'Archive',
  computed: {
    ...mapState(["cardData", "cardType", "cardAuthorStr", "cardSource", "authorData", "archiveIs404", "archiveIs500", "searchQuery", "archiveIs429"]),
  },
  components: {NavbarRed, SearchResults, Author, ArchiveItem, Alerts, ArchiveHome},
  props: ['path'],
  data() {
    return {}
  },
  methods: {
    async setData() {
      try {
        const fullPathParts = this.$route.fullPath.split("/").filter(function (e) {
          return e
        });

        if (fullPathParts.length === 0) {
          // This happens when the home page is loaded.
          return
        }

        const siteIdentifier = fullPathParts[0] === "character" ? "generic" : fullPathParts[0]
        const handler = initializeHandler(siteIdentifier, null, false)
        if (handler == null) {
          this.trigger404()
          return
        }

        if ((fullPathParts[0] !== "generic" && fullPathParts.length === 2) || (fullPathParts[0] === "generic" && fullPathParts[1].split("+").length === 1)) { // begin author view
          const authorName = fullPathParts[1]
          if (!handler.hasAuthors) {
            this.trigger404()
            return
          }

          let response
          try {
            response = await axios.get(handler.resolveAuthorUrl(authorName))
          } catch (err) {
            if (err.response.data.code === 404) {
              this.trigger404()
            } else if (err.response.data.code === 429) {
              this.trigger429()
            } else {
              this.trigger500()
            }
            return
          }
          if (siteIdentifier === "generic" && response.data.characters.length === 0) {
            this.trigger404()
          }
          this.$store.commit("authorData", response.data)
          document.title = `Character Card Archive | ${handler.prettyName} - ${response.data.username}`
          return
        } // end author view

        if ((fullPathParts.length > 4 || fullPathParts.length < 2)) {
          this.trigger404()
          return
        }

        // Populate the required fields and set the backend API url to fetch.
        this.$store.commit('cardSource', handler.identifier)
        const loadInfo = handler.handleNodeLoad(fullPathParts)
        if (loadInfo == null) {
          this.trigger404()
          return
        }

        this.$store.commit('cardType', loadInfo.type)
        if (loadInfo.author != null) {
          this.$store.commit('cardAuthorStr', loadInfo.author)
        }

        let response
        try {
          response = await axios.get(`${APIHOST}/api/archive/v1/${loadInfo.apiUrl}`)
        } catch (err) {
          if (err.response.data.code === 404) {
            this.trigger404()
          } else if (err.response.data.code === 429) {
            this.trigger429()
          } else {
            this.trigger500()
          }
          return
        }
        this.$store.commit('cardData', response.data)
      } catch (error) {
        console.error(`Failed to load page "${this.$route.fullPath}" - ${error}`)
        this.trigger500()
      }
    },
    resetData() {
      this.$store.commit('archiveIs404', false)
      this.$store.commit('archiveIs500', false)
      this.$store.commit('archiveIs429', false)
      this.$store.commit('cardAuthorStr', "")
      this.$store.commit('cardType', "")
      this.$store.commit('cardData', {})
      this.$store.commit('cardSource', "")
      this.$store.commit('authorData', {})
      this.$store.commit('searchQuery', " ")
      document.title = "Character Card Archive"
    },
    trigger404() {
      this.$store.commit('archiveIs404', true)
      document.title = `Character Card Archive`
      console.error("404 Not Found", this.$route.fullPath)
    },
    trigger500() {
      this.$store.commit('archiveIs500', true)
      document.title = `Character Card Archive`
      console.error("500 Internal Server Error", this.$route.fullPath)
    },
    trigger429() {
      this.$store.commit('archiveIs429', true)
      document.title = `Character Card Archive`
      console.error("429 Too Many Requests", this.$route.fullPath)
    },
    trackPageView() {
      if (document.title !== "Character Card Archive") {
        _paq.push(['setCustomUrl', window.location.href])
        _paq.push(['setDocumentTitle', document.title])
        _paq.push(['trackPageView'])
      }
    },
  },
  async mounted() {
    this.resetData()
    await this.setData()
    this.trackPageView()
  },
  created() {
    window.scrollTo(0, 0)
  },
  watch: {
    '$route': async function (to, from) {
      // Check if we are going to a different page.
      // All our other pages end with .html to keep things simple.
      const checkOtherPage = to.fullPath.match(/^\/.*?\.html/)
      if (!checkOtherPage && (to.path !== from.path || to.query.page !== from.query.page)) {
        window.scrollTo(0, 0)
        this.resetData()
        await this.setData()
        this.trackPageView()
      }
    },
  }
};
</script>

<style scoped>
@import '@/assets/css/front.css';
@import '@/assets/css/archive.css';
@import '@/assets/css/loader.css';
</style>
