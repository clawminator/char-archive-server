<template>
  <div class="flex action-group mt-[71px] absolute">
    <div
        class="action-box max-md:p-2.5 flex max-md:justify-center max-md:items-center md:flex-col md:items-end max-md:w-screen">
      <button aria-label="Download" class="action" title="Download"
              v-bind:disabled="getDisabledDownloadDirs()"
              @click="downloadDirectory">
        <i class="material-icons">file_download</i>
      </button>
      <button aria-label="Info" class="action max-md:pl-5 max-md:pr-5" title="Info" @click="showFolderInfo">
        <i class="material-icons">info</i>
      </button>
    </div>
  </div>

  <Spinner/>

  <div :key="`filebrowser-root-${currentPath}`" class="front-container scroll md:mt-3">
    <div class="home-search w-full mt-3">
      <form class="w-full mx-auto" @submit.prevent="doSearch">
        <label class="mb-2 text-sm font-medium text-gray-900 sr-only" for="default-search">Search</label>
        <div class="relative mx-3 max-md:my-10">
          <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
            <svg aria-hidden="true" class="w-4 h-4 text-gray-500 dark:text-gray-400"
                 fill="none" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z" stroke="currentColor" stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"/>
            </svg>
          </div>
          <input id="searchfield"
                 v-model="searchfieldValue"
                 :disabled="siteDisabled"
                 autocomplete="off"
                 class="outline-none focus:ring-0 filebrowser-search block w-full p-4 ps-10 text-sm text-gray-900 rounded-lg bg-white"
                 placeholder="Search..." required
                 type="search"
          />
          <button
              class="text-white absolute end-2.5 bottom-2.5 bg-red-800 hover:bg-red-700 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-4 py-2"
              type="submit">
            Search
          </button>
        </div>
      </form>
    </div>

    <div class="directory-path flex items-center max-md:text-2xl md:text-lg sm:mt-4 max-md:justify-center">
      <a class="flex items-center" @click="navigateToPath('/', -1)">
        <i class="material-icons align-middle">home</i>
      </a>
      <!--      <span class="path-separator">/</span>-->
      <span v-for="(part, index) in currentPath.split('/')" :key="`path-separator-${index}`"
            class="flex items-center">
        <a @click="navigateToPath(part, index)">{{ part }}</a>
        <span v-if="index < currentPath.split('/').length - 1" class="path-separator">/</span>
      </span>
    </div>
    <div class="bg-gray-100 box-border flex flex-row space-x-1 my-4 scroll">
      <div class="bg-white rounded shadow p-4 justify-center w-full">
        <div class="bg-white rounded shadow p-4">
          <div class="grid grid-cols-4 gap-5 py-2 border-b border-gray-200 file-header">
            <p class="file-column col-span-1 auto-cols-max left-column" @click="sortFilesClick('name')">Name</p>
            <p class="file-column col-span-1 text-center center-column hidden md:block"
               @click="sortFilesClick('modified')">Last
              Modified</p>
            <p class="file-column col-span-1 text-center right-column hidden md:block" @click="sortFilesClick('size')">
              Size</p>
          </div>
          <ul class="divide-y divide-gray-200">
            <li v-for="file in files" :key="`fileitem-${file.path}`" :data-path="file.path"
                class="py-4 grid grid-cols-4 gap-5"
                style="cursor: pointer"
                @click="navigateTo(file)">
              <div class="flex space-x-2 items-center auto-cols-max">
                <i v-if="file.isDir" class="material-icons folder-icon">folder</i>
                <i v-else class="material-icons folder-icon">text_snippet</i>
                <p class="font-medium filename left-column">
                  {{ file.name }}
                </p>
              </div>
              <p class="text-sm text-gray-700 col-span-1 text-center center-column hidden md:block">
                {{ FormatDate(file.modified) }}</p>
              <p class="text-sm text-gray-700 col-span-1 text-center right-column hidden md:block">{{
                  !file.isDir ? FormatSize(file.size) : '-'
                }}</p>
            </li>
            <li v-for="i in 3" v-if="showLoadingPlaceholder" :key="`placeholder-${i}`"
                class="py-4 grid grid-cols-4 gap-5 cursor-wait">
              <div class="flex space-x-2 items-center auto-cols-max">
                <span class="w-1/2 min-h-[1em] bg-gray-200 animate-pulse"></span>
              </div>
              <p class="text-sm text-gray-700 col-span-1 text-center center-column hidden md:block"><span
                  class="inline-block w-1/10 min-h-[1em] bg-gray-200 animate-pulse"></span></p>
              <p class="text-sm text-gray-700 col-span-1 text-center right-column hidden md:block"><span
                  class="inline-block w-1/10 min-h-[1em] bg-gray-200 animate-pulse"></span></p>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <nav aria-label="Page navigation" class="mb-4">
      <div class="flex flex-col md:flex-row items-start max-md:items-center">
        <ul class="list-style-none flex max-md:justify-center md:my-4 max-md:mt-4 select-none">
          <li>
            <router-link
                :class="currentPage === 1 ? 'pointer-events-none relative block rounded bg-transparent px-3 py-1.5 text-sm text-neutral-500 transition-all duration-300 dark:text-neutral-400' : 'relative block rounded bg-transparent px-3 py-1.5 text-sm text-neutral-600 transition-all duration-300 hover:bg-neutral-100  dark:text-white dark:hover:bg-neutral-700 text-red-primary-hover'"
                :to="{ name: 'Files', query: {path: currentPath, page: currentPage > 1 ? currentPage - 1 : 1 } }"
            >&larr; Previous
            </router-link>
          </li>
          <li v-for="(page, index) in displayedPages" :key="`pagenumber-${index}-${page}`">
            <router-link
                v-if="typeof page === 'number'"
                :class="{
                  'relative block rounded px-3 py-1.5 text-sm transition-all duration-300': true,
                  'bg-primary-200 font-medium text-red-primary': parseInt(currentPage) === page,
                  'bg-transparent text-neutral-600 hover:bg-neutral-100 dark:text-white dark:hover:bg-neutral-700 dark:hover:text-white text-red-primary-hover': parseInt(currentPage) !== page
                }" :to="{ name: 'Files', query: {path: currentPath, page: page } }"
            >{{ page }}
            </router-link>
            <span v-else>...</span>
          </li>
          <li>
            <router-link
                :class="currentPage === totalPages ? 'pointer-events-none relative block rounded bg-transparent px-3 py-1.5 text-sm text-neutral-500 transition-all duration-300 dark:text-neutral-400' : 'relative block rounded bg-transparent px-3 py-1.5 text-sm text-neutral-600 transition-all duration-300 hover:bg-neutral-100 dark:text-white dark:hover:bg-neutral-700 dark:hover:text-white text-red-primary-hover'"
                :to="{ name: 'Files', query: { path: currentPath, page: currentPage < totalPages ? currentPage + 1 : totalPages } }"
            >Next &rarr;
            </router-link>
          </li>
        </ul>
        <div class="my-4 md:ml-2">
          <input
              v-model="inputPage"
              :max="totalPages"
              class="px-2 py-1 w-40 red-input rounded"
              min="1"
              placeholder="Go to page..."
              type="number"
              @keyup.enter="goToPage"
          />
          <button
              class="ml-2 px-2 py-1 md:hidden bg-primary-400 bg-primary-hover text-red-primary font-bold hover:text-white rounded"
              @click="goToPage"
          >
            Go
          </button>
        </div>
      </div>
    </nav>
  </div>

  <Alerts/>
  <FileBrowserModals/>
</template>

<script>
import {matoPush} from "@/assets/js/mato";
import axios from "axios";
import {removeItem} from "@/assets/js/array";
import Spinner from "@/components/parts/Spinner.vue";
import FileBrowserModals from "@/components/parts/filebrowser/browserModals.vue";
import {FormatDate, FormatSize} from "@/assets/js/date";
import {APIHOST} from "@/components/config"
import Alerts from "../Alerts.vue";
import {mapState} from "vuex";
import {ScrollToDataPathElement} from "@/assets/js/scroll";
import {initFlowbite} from "flowbite";
import {scanMsg} from "@/assets/js/messages";
import naturalCompare from 'natural-compare-lite';


// TODO: this page does not show the loading placeholders when entering it directly from pasting url in address bar: https://chub-archive.example.com/#/chub.ai/characters/bipbop
// TODO: the path query arg is erased on load

export default {
  name: 'Filebrowser',
  components: {Alerts, FileBrowserModals, Spinner},
  data() {
    return {
      currentPath: this.$route.query.path || "/",
      files: [],
      sortedFileList: [],
      currentSort: 'name',
      currentSortDir: 'asc',
      page: 1,
      limit: 50,
      currentPage: this.$route.query.page || 1,
      totalPages: 1, // this used to be set to -1 to indicate a null state but we're defaulting to one page now.
      userSort: 'name',
      healthCheckInterval: null,
      scanMsgDismissed: false,
      inputPage: null,
      restrictedDownloadDirs: [],
      checkedRestrictedDownloadDirs: false,
      currentRequest: null,
      fetchDataInProgress: false,
      searchInputActive: false,
      searchfieldValue: '',
    }
  },
  methods: {
    FormatDate,
    FormatSize,
    async doSearch() {
      document.activeElement.blur();
      this.$store.commit('showSpinner', true);
      try {
        const response = await fetch(`${APIHOST}/api/file/search?query=${this.searchfieldValue}&exclude=.git&sort=folders&fields=name`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        _paq.push(['trackSiteSearch', this.searchfieldValue, false, data.results.length]);

        this.$store.commit('searchResults', data.results)
        this.$store.commit("searchQuery", this.searchfieldValue)
        this.$store.commit('showSearchModal', true)
      } catch (error) {
        this.$store.commit('addAlert', 'There was a problem with the fetch operation: ' + error);
        console.error('There was a problem with the fetch operation: ', error);
      }
      this.$store.commit('showSpinner', false);
    },
    navigateToPath(targetDir, index) {
      let newPath;
      if (index === -1) {
        newPath = '/';
      } else {
        const pathParts = this.currentPath.split('/');
        newPath = pathParts.slice(0, index + 1).join('/');
      }
      this.appendQueryParameter("path", newPath);
    },
    showFolderInfo() {
      // this.$store.commit('sharedCurrentPathData', this.currentFolderData);
      this.$store.commit('setFolderModalVisibility', true);
    },
    sortFiles(files) {
      return files.sort((a, b) => {
        // Folders are ALWAYS sorted before files.
        if (a.isDir !== b.isDir) {
          return a.isDir ? -1 : 1;
        }

        // Compare names using natural-compare-lite.
        const nameComparison = naturalCompare(a.name.toLowerCase(), b.name.toLowerCase());
        if (nameComparison !== 0) {
          return this.currentSortDir === 'asc' ? nameComparison : -nameComparison;
        }

        // Don't remember why this is here.
        // // Convert booleans to numbers
        // const aNum = typeof aValue === 'boolean' ? (aValue ? 1 : 0) : aValue;
        // const bNum = typeof bValue === 'boolean' ? (bValue ? 1 : 0) : bValue;
        // // Compare values
        // if (aNum < bNum) return this.currentSortDir === 'asc' ? -1 : 1;
        // if (aNum > bNum) return this.currentSortDir === 'asc' ? 1 : -1;

        return 0;
      });
    },
    sortFilesClick(column) {
      this.userSort = column;
      if (this.currentSort === column) {
        this.currentSortDir = this.currentSortDir === 'asc' ? 'desc' : 'asc';
      } else {
        this.currentSort = column;
        this.currentSortDir = 'asc';
      }
      this.files = this.sortFiles(this.files);
    },
    getDisabledDownloadDirs() {
      return !this.checkedRestrictedDownloadDirs || this.restrictedDownloadDirs.includes(this.currentPath)
    },
    navigateTo(file) {
      let path = file.path;
      if (file.isDir) {
        this.appendQueryParameter("path", path)
      } else {
        this.downloadFile(file.path);
      }
    },
    formPageTitle() {
      return `Character Card Archive | Files - ${this.currentPath}`;
    },
    async downloadDirectory() {
      const targetUrl = `${APIHOST}/api/file/download?path=${this.currentPath}`

      _paq.push(['trackLink', targetUrl, 'download']);
      matoPush('User Interface', 'Download Folder', this.currentPath);

      window.open(targetUrl, '_blank');
    },
    goToPage() {
      if (this.inputPage >= 1 && this.inputPage <= this.totalPages) {
        document.activeElement.blur();
        this.currentPage = this.inputPage
        this.appendQueryParameter("path", this.currentPath)
        this.appendQueryParameter("page", this.inputPage)
        if (this.inputPage === 1) {
          this.removeQueryParameter("page")
        }
        this.inputPage = null
      }
    },
    async makeRequest(apiPath) {
      if (this.currentRequest) {
        console.log('Operation canceled due to new request.')
        this.currentRequest.cancel('Operation canceled due to new request.')
      }

      const source = axios.CancelToken.source();
      this.currentRequest = source;

      this.$store.commit('showSpinner', true)
      const targetURL = `${APIHOST}${apiPath}`;
      try {
        let response;
        response = await axios.get(targetURL, {
          cancelToken: source.token
        });
        return response.data;
      } catch (error) {
        if (axios.isCancel(error)) {
          console.debug(`makeRequest() - our request to was canceled: "${targetURL}"`)
          return error
        } else {
          const msg = 'There was a problem with the fetch operation: ' + error.code + " - " + error.message
          console.error(msg);
          this.$store.commit('addAlert', msg);
        }
      } finally {
        this.$store.commit('showSpinner', false)
        this.currentRequest = null
      }
    },
    async fetchData() {
      if (this.currentRequest !== null) {
        return
      }

      this.$store.commit('showLoadingPlaceholder', true);

      let raw = null;
      try {
        raw = await this.makeRequest(`/api/file/list?path=${this.currentPath}&page=${this.currentPage}&limit=50&sort=folders`);
      } catch (error) {
        if (axios.isCancel(error)) {
          console.log('fetchData() - our request was canceled: ', error.message)
          return
        } else {
          console.error('Failed to fetch files: ' + error)
        }
      } finally {
        this.$store.commit('showLoadingPlaceholder', false)
      }

      if (axios.isCancel(raw)) {
        console.debug("fetchData was canceled")
        await this.fetchData() // Retry the fetch if the request was canceled
        return
      }
      if (raw != null) {
        this.totalPages = raw.total_pages;
        const data = raw.item;
        this.$store.commit('sharedCurrentPathData', data);
        this.files = this.sortFiles([...data.children]); // Sort the new data
      }
      if (this.scrollToDataPath != null) {
        await this.$nextTick(() => {
          ScrollToDataPathElement(this.scrollToDataPath)
          this.$store.commit('scrollToDataPath', null)
        });
      }
    },
    async fetchRestrictedDownloads() {
      try {
        const raw = await axios.get(`${APIHOST}/api/file/client/restricted-download`);
        if (raw != null) {
          this.restrictedDownloadDirs = raw.data;
          this.checkedRestrictedDownloadDirs = true;
        } else {
          console.error("fetchRestrictedDownloads() got no data")
        }
      } catch (error) {
        const msg = 'Failed to get restricted download directories: ' + error.code + " - " + error.message
        console.error(msg);
        this.$store.commit('addAlert', msg);
      }
    },
    downloadFile(filePath) {
      this.$store.commit('showSpinner', true);
      const fileName = filePath.split('/').pop();
      try {
        const url = `${APIHOST}/api/file/download?path=${filePath}&download=true`;
        var element = document.createElement('a');
        element.setAttribute('href', url);
        element.setAttribute('download', fileName);
        element.setAttribute('target', "_blank");
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);

        // saveAs(url, fileName);
      } catch (error) {
        const errMsg = 'There was a problem with the fetch operation: ' + error.code + " - " + error.message
        this.$store.commit('addAlert', errMsg);
        console.error(errMsg);
      }
      this.$store.commit('showSpinner', false);
    },
    lockSite(msg) {
      if (!this.siteDisabled) {
        console.error(`Site locked`)
        this.$store.commit('siteDisabled', true)
        this.$store.commit('clearAlerts')
        document.body.classList.add("site-disabled")
        this.$store.commit("sharedSiteLockMsg", msg)
        this.$store.commit("siteDisabled", true)
      }
    },
    unlockSite() {
      if (this.siteDisabled) {
        console.log('Site unlocked')
        this.$store.commit('siteDisabled', false)
        this.$store.commit('clearAlerts')
        document.body.classList.remove("site-disabled")
        this.$store.commit("sharedSiteLockMsg", null)
        this.$store.commit("siteDisabled", true)
      }
    },
    disableSite() {
      this.lockSite("disabled");
    },
    disableSiteInitialCrawl() {
      this.$store.commit("sharedSiteLockMsg", "scanning")
    },
    async checkBackendHealth() {
      let apiStatusCode;
      let apiRes;
      try {
        apiRes = await axios.get(`${APIHOST}/api/file/client/health`)
        if (apiRes == null) {
          this.disableSite()
        } else {
          apiStatusCode = apiRes.status
          if (apiRes.data.initialScanRunning) {
            this.disableSiteInitialCrawl()
          } else if (apiStatusCode !== 200) {
            console.error("Got bad status code:", apiStatusCode)
            this.disableSite()
          } else if (apiRes.data.scanRunning) {
            console.log("Backend is running a scan")
            // this.addScanningMsg();
          } else if (!apiRes.data.scanRunning) {
            if (this.$store.getters.statusExists(scanMsg)) {
              console.log("Backend finished a scan")
              removeItem(this.showStatus, scanMsg);
            }
            this.unlockSite(); // Unlock the site when it's healthy
          }
        }
      } catch (err) {
        console.error(err)
        this.disableSite()
      }
    },
    trackPageView() {
      if (document.title !== "Character Card Archive") {
        _paq.push(['setDocumentTitle', this.formPageTitle()])
        _paq.push(['setCustomUrl', window.location.href])
        _paq.push(['trackPageView'])
      }
    },
    appendQueryParameter(param, value) {
      let query = Object.assign({}, this.$route.query)
      query[param] = value
      this.$router.push({query: query}).catch(err => {
      })
    },
    removeQueryParameter(param) {
      let query = Object.assign({}, this.$route.query)
      delete query[param]
      this.$router.push({query: query}).catch(err => {
      })
    },
  },
  computed: {
    displayedPages() {
      const range = 2; // number of pages to display before and after the current page
      let pages = [];

      for (let i = 1; i <= this.totalPages; i++) {
        if (i === 1 || i === this.totalPages || (i >= this.currentPage - range && i <= this.currentPage + range)) {
          pages.push(i);
        } else if (i === this.currentPage - range - 1 || i === this.currentPage + range + 1) {
          pages.push('...');
        }
      }
      return pages;
    },
    ...mapState(['scrollToDataPath', "siteDisabled", "showLoadingPlaceholder", "sharedCurrentPath", "sharedCurrentPathData"])
  },
  async mounted() {
    this.$store.commit('showSpinner', true)
    this.healthCheckInterval = setInterval(this.checkBackendHealth, 60000);
    await this.$nextTick(() => {
      initFlowbite()
    })
  },
  async created() {
    if (this.currentPage > 1) {
      // If the user set the page query arg tp more than one, update the view.
      this.appendQueryParameter("page", this.currentPage)
    } else {
      // If the user doesn't have the page query arg or it equals one, remove it from the URL
      this.removeQueryParameter("page")
    }

    this.$store.commit('sharedCurrentPath', this.currentPath)
    this.$store.commit('sharedCurrentPage', this.currentPage)

    this.currentSortDir = 'desc'
    this.sortFilesClick('name') // Sort files by name when the page loads
    await this.checkBackendHealth()
    await this.fetchRestrictedDownloads()
    if (this.files.length === 0) {
      // Sometimes the data isn't loaded.
      await this.fetchData()
    }
    this.trackPageView()
  },
  destroyed() {
    document.getElementById("searchfield").value = "" // TODO: fix this
    clearInterval(this.healthCheckInterval);
    window.removeEventListener('resize', this.handleResize);
  },
  watch: {
    files(newVal, oldVal) {
      this.files = this.sortFiles(newVal);
    },
    '$route.query.path': {
      immediate: true,
      async handler(newPath) {
        if (newPath === undefined || newPath === null) {
          this.currentPath = "/"
        } else {
          this.currentPath = newPath
        }
        this.currentPage = 1;

        // Cancel the previous request
        if (this.currentRequest) {
          console.debug("Canceling current request")
          this.currentRequest.cancel('Operation canceled due to route change.');
          this.currentRequest = null;
        }

        window.scrollTo(0, 0);
        await this.fetchData();
        this.trackPageView();
      }
    },
    '$route.query.page': {
      immediate: true,
      async handler(newPage) {
        if (newPage === undefined || newPage === null) {
          this.currentPage = 1
        } else {
          this.currentPage = newPage
        }

        if (this.totalPages > 0 && newPage > this.totalPages && this.files.length > 0) {
          // Reset the current page in case something got messed up, but only if there are files in the file list, meaning
          // things are not currently loading.
          console.warn(`Refusing request because we've already loaded all the pagination. Requested page: ${newPage}. Total pages: ${this.totalPages}.`)
          this.currentPage = this.totalPages;
          this.inputPage = null;
          if (this.currentPage === 1) {
            this.removeQueryParameter("page")
          }
          this.$store.commit('sharedCurrentPage', this.currentPage)
          return
        }

        // Reset the existing stuff.
        window.scrollTo(0, 0)
        this.files = []
        this.inputPage = null
        if (this.currentPage === 1) {
          this.removeQueryParameter("page")
        }
        this.$store.commit('sharedCurrentPage', this.currentPage)

        // Load the new data.
        await this.fetchData()
        document.title = this.formPageTitle()
      }
    },
    'showLoadingPlaceholder': async function (newVal, oldVal) {
      if (newVal === true) {
        this.files = []
      }
    },
    "searchQuery": async function (newVal, oldVal) {
      // The `navigateFromSearchToFolder()` function will tell us when to clear the text input field.
      if (newVal === "") {
        document.getElementById("searchfield").value = ""
      }
    }
  },
}
</script>

<style scoped>
@import '@/assets/css/filebrowser.css';
@import '@/assets/css/front.css';
</style>
