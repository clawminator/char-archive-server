<template>
  <div class="w-full mx-auto">
    <div class="author-header flex items-center justify-center flex-col mx-auto mb-10">
      <div class="w-[200px] h-[200px] bg-gray-300 mx-auto shadow-lg rounded-lg flex items-center justify-center"
           v-html="resolveAvatarElm()"></div>
      <div v-if="resolveCardPrettyName() !== ''" class="mt-10 italic text-sm">
        {{ resolveCardPrettyName() }}
      </div>
      <h1 class="inline-flex items-center text-4xl font-bold mt-3 prose">
        {{ authorData.username }}
        <a v-if="resolveCardPrettyName() !== '' && resolveAuthorExternalUrl() != null"
           :href="resolveAuthorExternalUrl()"
           class="hover:bg-[unset] inline-flex unset-a-style"
           target="_blank">
          <Popper :content="`View on ${resolveCardPrettyName()}`" arrow hover>
            <span class="inline-flex material-icons ml-3 cursor-pointer-force">open_in_new</span>
          </Popper>
        </a>
      </h1>

      <div class="mt-5 mb-10">
        <Popper arrow content="Download author JSON" hover>
          <button
              class="bg-green-800 mx-auto w-32 h-10 inline-flex justify-center items-center rounded-md py-1 px-2 text-sm font-semibold text-white shadow-lg"
              @click="downloadAuthorData()">
            <span class="material-icons cursor-pointer-force">data_object</span>
            <span class="font-extrabold text-lg force-h-16">&nbsp;JSON</span>
          </button>
        </Popper>
      </div>

      <div v-if="handler.resolveAuthorBio(authorData) != null"
           class="prose bg-white shadow-lg rounded-lg w-full h-full p-3 max-md:max-w-[90%] lg:max-w-[70%] my-10"
           v-html="parseUntrustedHTML(handler.resolveAuthorBio(authorData))"></div>
    </div>

    <div>
      <h1 class="text-4xl font-extrabold text-center mb-7 mt-20">Characters</h1>
      <p v-if="displayedCharacterPages.length === 0" class="text-center"> No characters.</p>
      <div v-else>
        <div class="flex justify-center">
          <label class="mb-2 text-sm font-medium text-gray-900 flex items-center" for="char-sorting">Sort By</label>
          <select id="char-sorting" v-model="sortCharsOption"
                  class="inline bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 m-3"
                  @change="sortAuthorData('characters', sortCharsOption, true)">
            <option selected value="name">Name</option>
            <option value="created">Date</option>
            <option v-if="authorData.characters[0]?.downloads != null" value="downloads">Downloads</option>
          </select>
          <span class="inline-flex material-icons ml-3 cursor-pointer-force select-none items-center"
                @click="toggleSortDirection('characters')">
          {{ sortDirectionChars === 'asc' ? 'arrow_downward' : 'arrow_upward' }}
        </span>
        </div>
        <div class="char-list grid gap-4 w-full max-sm:p-8">
          <li v-for="card in paginatedCharacters" :key="`char-${card.id}`"
              :class="[resolveCardColor(card), {'bg-gray-300' : card.placeholder !== undefined}]"
              class="char-list-item py-4 rounded mb-5">
            <div class="flex flex-col items-center h-full">
              <div class="char-item-grid h-full flex flex-col justify-between">
                <div class="char-list-avatar flex items-center rounded m-auto">
                  <a :href="resolveCardLink(card, 'character')" class="bg-gray-200 w-[200px] h-[200px] rounded">
                    <img :src="resolveAvatarURL(card, 'character')" alt="" class="rounded"
                         onerror="this.src='/img/thumbnail-failure-200.png'">
                  </a>
                </div>
                <div class="h-full">
                  <p class="char-list-name text-center mt-[5px]">
                    <a :href="resolveCardLink(card, 'character')">
                      {{ limitString(card.name, nameLengthLimit) }}
                    </a>
                  </p>
                  <p class="char-list-desc">
                    <div class="text-center font-bold mb-3">
                      {{ DateTime.fromISO((card.created == null) ? card.added : card.created).toLocaleString(DateTime.DATETIME_MED) }}
                    </div>
                    <a :href="resolveCardLink(card, 'character')">
                      {{ limitString(card.tagline, descLengthLimit) }}
                    </a>
                  </p>
                </div>
              </div>
              <div v-if="card.source === 'generic'" class="char-list-source-container w-full">
                <div class="char-list-source w-full">
                  {{ resolveCardPrettyName(card) }}
                </div>
              </div>
            </div>
          </li>
        </div>
        <nav aria-label="Character Page navigation" class="my-5">
          <div class="flex flex-col md:flex-row items-start max-md:items-center">
            <div class="flex mx-auto">
              <ul class="list-style-none flex max-md:justify-center md:my-4 max-md:mt-4 select-none">
                <li>
                  <button
                      :class="pagination.characters.currentPage === 1 ? 'pointer-events-none' : 'hover:bg-neutral-100'"
                      :disabled="pagination.characters.currentPage === 1"
                      class="mr-2 px-2 py-1 bg-primary-400 bg-primary-hover text-red-primary font-bold hover:text-white rounded"
                      @click="pagination.characters.currentPage--"
                  >
                    &larr;
                  </button>
                </li>
                <li v-for="(page, index) in displayedCharacterPages" :key="`pagenumber-${index}-${page}`">
                  <button
                      v-if="page !== '...'"
                      :class="pagination.characters.currentPage === page ? 'relative block rounded bg-primary-200 px-3 py-1.5 text-sm font-medium text-red-primary transition-all duration-300' : 'relative block rounded bg-transparent px-3 py-1.5 text-sm text-neutral-600 transition-all duration-300 hover:bg-neutral-100  dark:text-white dark:hover:bg-neutral-700 dark:hover:text-white text-red-primary-hover'"
                      @click="pagination.characters.currentPage = page"
                  >
                    {{ page }}
                  </button>
                  <span v-else>...</span>
                </li>
                <li>
                  <button
                      :class="pagination.characters.currentPage === totalCharacterPages ? 'pointer-events-none' : 'hover:bg-neutral-100'"
                      :disabled="pagination.characters.currentPage === totalCharacterPages"
                      class="ml-2 px-2 py-1 bg-primary-400 bg-primary-hover text-red-primary font-bold hover:text-white rounded"
                      @click="pagination.characters.currentPage++"
                  >
                    &rarr;
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </nav>
      </div>
    </div>

    <div v-if="authorData.source === 'chub'">
      <h1 class="text-4xl font-extrabold text-center mb-7 mt-20">Lorebooks</h1>
      <p v-if="displayedLorebookPages.length === 0" class="text-center"> No lorebooks.</p>
      <div v-else>
        <div class="flex justify-center">
          <label class="mb-2 text-sm font-medium text-gray-900 flex items-center" for="char-sorting">Sort By</label>
          <select id="char-sorting" v-model="sortBooksOption"
                  class="inline bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 m-3"
                  @change="sortAuthorData('lorebooks', sortBooksOption, true)">
            <option selected value="name">Name</option>
            <option value="created">Date</option>
            <option v-if="authorData.lorebooks[0]?.downloads != null" value="downloads">Downloads</option>
          </select>
          <span class="inline-flex material-icons ml-3 cursor-pointer-force select-none items-center"
                @click="toggleSortDirection('lorebooks')">
          {{ sortDirectionBooks === 'asc' ? 'arrow_downward' : 'arrow_upward' }}
        </span>
        </div>
        <div class="char-list grid gap-4 w-full max-sm:p-8">
          <li v-for="book in paginatedLorebooks" :key="`book-${book.id}`"
              :class="[resolveCardColor(book), {'bg-gray-300' : book.placeholder !== undefined}]"
              class="char-list-item py-4 rounded mb-5">
            <div class="flex flex-col items-center">
              <div class="char-item-grid w-full">
                <div class="char-list-avatar flex items-center rounded m-auto">
                  <a :href="resolveCardLink(book, 'lorebook')" class="bg-gray-200 w-[200px] h-[200px] rounded">
                    <img :src="resolveAvatarURL(book, 'lorebook')" alt="" class="rounded"
                         onerror="this.src='/img/thumbnail-failure-200.png'">
                  </a>
                </div>
                <div>
                  <p class="char-list-name text-center mt-[5px]">
                    <a :href="resolveCardLink(book, 'lorebook')">
                      {{ limitString(book.name, nameLengthLimit) }}
                    </a>
                  </p>
                  <p class="char-list-desc">
                    <div class="text-center font-bold mb-3">
                      {{ DateTime.fromISO(book.created).toLocaleString(DateTime.DATETIME_MED) }}
                    </div>
                    <a :href="resolveCardLink(book, 'lorebook')">
                      {{ limitString(book.tagline, descLengthLimit) }}
                    </a>
                  </p>
                </div>
              </div>
            </div>
          </li>
        </div>
        <nav aria-label="Lorebook Page navigation" class="my-5">
          <div class="flex flex-col md:flex-row items-start max-md:items-center">
            <div class="flex mx-auto">
              <ul class="list-style-none flex max-md:justify-center md:my-4 max-md:mt-4 select-none">
                <li>
                  <button
                      :class="pagination.lorebooks.currentPage === 1 ? 'pointer-events-none' : 'hover:bg-neutral-100'"
                      :disabled="pagination.lorebooks.currentPage === 1"
                      class="mr-2 px-2 py-1 bg-primary-400 bg-primary-hover text-red-primary font-bold hover:text-white rounded"
                      @click="pagination.lorebooks.currentPage--"
                  >
                    &larr;
                  </button>
                </li>
                <li v-for="(page, index) in displayedLorebookPages" :key="`pagenumber-${index}-${page}`">
                  <button
                      v-if="page !== '...'"
                      :class="pagination.lorebooks.currentPage === page ? 'relative block rounded bg-primary-200 px-3 py-1.5 text-sm font-medium text-red-primary transition-all duration-300' : 'relative block rounded bg-transparent px-3 py-1.5 text-sm text-neutral-600 transition-all duration-300 hover:bg-neutral-100  dark:text-white dark:hover:bg-neutral-700 dark:hover:text-white text-red-primary-hover'"
                      @click="pagination.lorebooks.currentPage = page"
                  >
                    {{ page }}
                  </button>
                  <span v-else>...</span>
                </li>
                <li>
                  <button
                      :class="pagination.lorebooks.currentPage === totalLorebookPages ? 'pointer-events-none' : 'hover:bg-neutral-100'"
                      :disabled="pagination.lorebooks.currentPage === totalLorebookPages"
                      class="ml-2 px-2 py-1 bg-primary-400 bg-primary-hover text-red-primary font-bold hover:text-white rounded"
                      @click="pagination.lorebooks.currentPage++"
                  >
                    &rarr;
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from "vuex";
import {APIHOST, CardDescLengthLimit, CardNameLengthLimit} from "@/components/config"
import {saveAs} from "file-saver";
import {initFlowbite} from "flowbite";
import {doubleEncodeUrlParam, limitString, parseUntrustedHTML} from "@/assets/js/strings";
import Popper from "vue3-popper";
import '@/assets/css/popper.css';
import {matoPushDl} from "@/assets/js/mato";
import {parseMarkdown} from "@/assets/js/markdown";
import {DateTime} from "luxon";
import {initializeHandler} from "@/assets/js/source-handler/initialize";

export default {
  name: 'Author',
  components: {Popper},
  data() {
    return {
      cardDefStr: "",
      nameLengthLimit: CardNameLengthLimit,
      descLengthLimit: CardDescLengthLimit,
      sortCharsOption: "name",
      sortBooksOption: "name",
      sortDirectionChars: "asc",
      sortDirectionBooks: "asc",
      pagination: {
        characters: {
          currentPage: 1,
          itemsPerPage: 10,
        },
        lorebooks: {
          currentPage: 1,
          itemsPerPage: 10,
        },
      },
    }
  },
  computed: {
    DateTime() {
      return DateTime
    },
    paginatedCharacters() {
      const start = (this.pagination.characters.currentPage - 1) * this.pagination.characters.itemsPerPage
      const end = start + this.pagination.characters.itemsPerPage
      return this.authorData.characters.slice(start, end)
    },
    paginatedLorebooks() {
      const start = (this.pagination.lorebooks.currentPage - 1) * this.pagination.lorebooks.itemsPerPage
      const end = start + this.pagination.lorebooks.itemsPerPage
      return this.authorData.lorebooks.slice(start, end)
    },
    totalCharacterPages() {
      return Math.ceil(this.authorData.characters.length / this.pagination.characters.itemsPerPage)
    },
    totalLorebookPages() {
      return Math.ceil(this.authorData.lorebooks.length / this.pagination.lorebooks.itemsPerPage)
    },
    displayedCharacterPages() {
      return this.getDisplayedPages('characters')
    },
    displayedLorebookPages() {
      return this.getDisplayedPages('lorebooks')
    },
    handler() {
      return initializeHandler(this.authorData.source, this.authorData.sourceSpecific)
    },
    ...mapState(["authorData"]),
  },
  methods: {
    parseUntrustedHTML,
    parseMarkdown,
    limitString,
    resolveAvatarElm() {
      const handler = initializeHandler(this.authorData.source, this.authorData.sourceSpecific)
      let [avatarUrl, onErrUrl] = handler.resolveAuthorAvatar(this.authorData)
      if (onErrUrl == null) {
        onErrUrl = "img/thumbnail-failure-200.png"
      }

      return `<img id="userAvatar" alt="" class="rounded-lg p-1" src="${APIHOST}/${avatarUrl}" onerror="this.onerror=null; this.src='${onErrUrl}'">`
    },
    downloadAuthorData() {
      const url = `${APIHOST}/api/archive/v1/${this.authorData.source}/user/${doubleEncodeUrlParam(this.authorData.username)}`
      saveAs(url, `${this.authorData.username} -- ${this.authorData.source}.json`)
      matoPushDl(url)
    },
    resolveCardColor(card) {
      const handler = initializeHandler(card.source, card.sourceSpecific)
      return handler.cardColor
    },
    resolveCardLink(card) {
      if (card.placeholder !== undefined) {
        return
      }
      let c = JSON.parse(JSON.stringify(card))
      c.author = this.authorData.username
      const handler = initializeHandler(card.source, card.sourceSpecific)
      return handler.resolveCardLink(c)
    },
    resolveAvatarURL(card, itemType) {
      let c = JSON.parse(JSON.stringify(card))
      c.author = this.authorData.username
      const handler = initializeHandler(card.source, card.sourceSpecific)
      return handler.resolveCardAvatarURL(c, false, true, 200, true)
    },
    resolveCardPrettyName() {
      const handler = initializeHandler(this.authorData.source)
      return handler.prettyName
    },
    getDisplayedPages(type) {
      const range = 2
      const currentPage = this.pagination[type].currentPage
      const itemsPerPage = this.pagination[type].itemsPerPage
      const dataLength = this.authorData[type].length
      const totalPages = Math.ceil(dataLength / itemsPerPage);
      let pages = [];
      for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - range && i <= currentPage + range)) {
          pages.push(i);
        } else if (i === currentPage - range - 1 || i === currentPage + range + 1) {
          pages.push('...');
        }
      }
      return pages;
    },
    sortAuthorData(dataType, sortOption, doReset) {
      let sortFunc;
      switch (sortOption) {
        case "name":
          sortFunc = (a, b) => a.name.localeCompare(b.name);
          break
        case "created":
          sortFunc = (a, b) => DateTime.fromISO(b.created) - DateTime.fromISO(a.created)
          break
        case "downloads":
          sortFunc = (a, b) => b.downloads - a.downloads;
          break
      }

      let sortDirection
      if (doReset) {
        switch (dataType) {
          case "characters":
            this.sortDirectionChars = "asc"
            break
          case "lorebooks":
            this.sortDirectionBooks = "asc"
        }
      } else {
        switch (dataType) {
          case "characters":
            sortDirection = this.sortDirectionChars
            break
          case "lorebooks":
            sortDirection = this.sortDirectionBooks
        }
      }

      if (sortDirection === 'desc') {
        let originalSortFunc = sortFunc;
        sortFunc = (a, b) => originalSortFunc(b, a); // reverse the sort order
      }

      this.authorData[dataType].sort(sortFunc);
    },
    toggleSortDirection(dataType) {
      let sortOption
      switch (dataType) {
        case "characters":
          this.sortDirectionChars = this.sortDirectionChars === 'asc' ? 'desc' : 'asc'
          sortOption = this.sortCharsOption
          break
        case "lorebooks":
          this.sortDirectionBooks = this.sortDirectionBooks === 'asc' ? 'desc' : 'asc'
          sortOption = this.sortBooksOption
          break
      }
      this.sortAuthorData(dataType, sortOption)
    },
    resolveAuthorExternalUrl() {
      const handler = initializeHandler(this.authorData.source)
      if (handler.resolveAuthorExternalUrl(this.authorData) != null) {
        return handler.resolveAuthorExternalUrl(this.authorData)
      } else {
        return null
      }
    }
  },
  async mounted() {
    this.sortAuthorData('characters', this.sortCharsOption, true)
    this.sortAuthorData('lorebooks', this.sortBooksOption, true)
    await this.$nextTick(() => {
      initFlowbite()
    })
  },
  watch: {}
};
</script>

<style scoped>
@import '@/assets/css/archive.css';
@import '@/assets/css/char-list.css';
@import '@/assets/css/colors.css';
</style>
