<template>
  <div v-if="showFolderModal" aria-labelledby="modal-title" aria-modal="true" class="fixed z-60 inset-0 overflow-y-auto"
       role="dialog">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div aria-hidden="true" class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
      <span aria-hidden="true" class="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
      <div
          class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
              <h3 id="modal-title" class="text-lg leading-6 font-medium text-gray-900">
                Folder Info
              </h3>
              <div class="mt-2 prose">
                <h4>{{ sharedCurrentPathData.name }}</h4>
                <i class="my-4">{{ sharedCurrentPathData.path }}</i>
                <p class="mt-1">
                  <span class="font-bold">Last modified:</span> {{
                    FormatDate(sharedCurrentPathData.modified)
                  }}<br>
                  <span class="font-bold">Last Cached:</span>
                  {{ DateFromSeconds(sharedCurrentPathData.cached / 1000) }}<br>
                  <!--                <span class="font-bold">Mode:</span> {{ sharedCurrentPathData.mode }}<br>-->

                  <!--                  TODO: need to calculate the total number of children, not the current paginated children. -->
                  <!--                  TODO: also, the endpoint needs to return how many total childen when paginating -->
                  <span class="font-bold">Children:</span> {{ sharedCurrentPathData.children.length }}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
              class="bg-main-red mt-3 w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              type="button"
              @click="closeModals">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-if="showSearchModal" aria-labelledby="modal-title" aria-modal="true"
       class="fixed search-results-modal inset-0 overflow-y-auto"
       role="dialog">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div aria-hidden="true" class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
      <span aria-hidden="true" class="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
      <div
          class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:w-full h-full search-results">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
              <div class="flex justify-between items-center">
                <h3 id="modal-title" class="text-lg leading-6 font-medium text-gray-900">
                  Search Results
                </h3>
                <button class="text-gray-700 hover:text-gray-900 font-bold" @click="closeModals">
                  X
                </button>
              </div>
              <div class="mt-2">
                <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 overflow-auto max-h-[300px] sm:max-h-[500px]">
                  <ul>
                    <li v-for="result in searchResults" :key="`searchresults-${result.path}`">
                      <a style="cursor: pointer" v-bind:class="{ 'text-blue-600': result.isDir }"
                         @click="navigateFromSearchToFolder(result)">{{ result.path }}</a>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
              class="mt-3 w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-main-red text-base font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              type="button" @click="closeModals">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-if="siteLockMsg"
       class="error-overlay fixed inset-0 bg-gray-100 z-50 flex items-center justify-center backdrop-blur-xsm bg-opacity-50">
    <div class="error-overlay-inner bg-white rounded p-4 shadow-lg prose" v-html="siteLockMsg"></div>
  </div>
</template>

<script>
import {DateFromSeconds, FormatDate} from "@/assets/js/date"
import {matoPush} from "@/assets/js/mato"
import {mapState} from "vuex"
import {APIHOST, ItemsPerPage} from "@/components/config"
import axios from "axios"
import {ScrollToDataPathElement} from "@/assets/js/scroll"
import {siteLockedHTML, siteScanningHTML} from "@/assets/js/messages";

// TODO: add a query arg to define a search query so the user can navigate back to a search
// TODO: when viewing a search from a query, show that query in the search box

export default {
  name: 'FileBrowserModals',
  data() {
    return {
      siteLockMsg: null,
    }
  },
  computed: {
    ...mapState(['showSearchModal']),
    ...mapState(['showFolderModal']),
    ...mapState(['searchResults']),
    ...mapState(['searchQuery']),
    ...mapState(['sharedCurrentPath', "sharedCurrentPage", "sharedCurrentPathData", "sharedSiteLockMsg"]),
  },
  methods: {
    FormatDate, DateFromSeconds,
    checkAlertExists(msg) {
      return this.$store.getters.alertExists(msg);
    },
    closeModals() {
      this.$store.commit('setFolderModalVisibility', false);
      this.$store.commit('showSearchModal', false);
    },
    // showFolderInfo() {
    //   this.showFolderModal = true;
    //   matoPush('User Interface', 'Filebrowser', 'Folder Info');
    // },
    closeOnEsc(event) {
      if (event.key === 'Escape') {
        this.closeModals();
      }
    },
    async navigateFromSearchToFolder(file) {
      let targetPath;
      if (!file.isDir) {
        let x = file.path.split("/")
        x.length = x.length - 1
        targetPath = x.join("/")
      } else {
        targetPath = file.path
      }
      if (targetPath !== "/" && targetPath.startsWith("/")) {
        targetPath = targetPath.slice(1)
      }

      // Hide the search modal right away.
      this.$store.commit('showSearchModal', false)

      // Clear the files list and show the loading placeholders only if we are going to navigate away
      // from this directory after we resolve the file's page.
      if (targetPath !== this.sharedCurrentPath) {
        this.$store.commit('showLoadingPlaceholder', true)
      }

      if (!file.isDir) {
        // Determine what page the file is on.
        const [resolvedPage, totalPages] = await this.resolveFilePage(file)
        if (resolvedPage == null) {
          console.error("resolveFilePage() failed to return any result")
        }

        // Don't navigate away if we're already where we need to be.
        if (targetPath === this.sharedCurrentPath && resolvedPage === this.sharedCurrentPage) {
          if (totalPages > 1) {
            await this.$nextTick(() => {
              ScrollToDataPathElement(file.path)
              this.$store.commit('scrollToDataPath', null)
            });
          }
          this.$store.commit('showSearchModal', false)
          return
        }

        if (totalPages > 1) {
          // If there is more than one page, tell the file browser to scroll to the file when it's finished loading.
          this.$store.commit('scrollToDataPath', file.path)
        }

        this.$router.push({
          name: 'files',
          query: {page: resolvedPage, path: targetPath},
        });
      } else {
        // If we're going to navigate into a directory, we don't want to try to set a page.
        this.$router.push({
          name: 'Files',
          query: {path: targetPath},
        });
      }

      matoPush('User Interface', 'Search Results', targetPath)
      this.$store.commit("searchQuery", "");
    },
    async resolveFilePage(file) {
      const path = file.path
      let parts = path.split("/")
      parts.splice(-1)
      let parentPath
      if (parts.length === 1) {
        parentPath = "/"
      } else {
        parentPath = parts.join("/")
      }

      this.$store.commit('showSpinner', true)
      let response = null
      try {
        response = await axios.get(`${APIHOST}/api/file/list?path=${parentPath}&resolve=${file.name}&limit=${ItemsPerPage}`)
      } catch (error) {
        const msg = 'There was a problem with the fetch operation: ' + error.code + " - " + error.message
        console.error(msg)
        this.$store.commit('addAlert', msg)
      } finally {
        this.$store.commit('showSpinner', false)
      }

      if (response != null) {
        return [response.data.resolved_page, response.data.total_pages]
      }
    }
  },
  mounted() {
  },
  created() {
    window.addEventListener('keydown', this.closeOnEsc);
  },
  beforeDestroy() {
    this.closeModals()
  },
  watch: {
    'sharedSiteLockMsg': async function (newVal, oldVal) {
      if (newVal === "disabled") {
        this.siteLockMsg = siteLockedHTML
      } else if (newVal === "scanning") {
        this.siteLockMsg = siteScanningHTML
      } else {
        this.siteLockMsg = newVal
      }
    }
  }
}
</script>

<style scoped>
@import '@/assets/css/filebrowser.css';
</style>
