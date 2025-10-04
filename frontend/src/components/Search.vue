<template>
  <NavbarRed/>
  <h1 class="text-4xl font-extrabold text-center mb-7 mt-20">Search Results</h1>
  <div class="my-10 sm:w-full max-sm:mx-3">
    <form class="max-w-md mx-auto" @submit.prevent="doSearch">
      <label class="mb-2 text-sm font-medium text-gray-900 sr-only dark:text-white"
             for="default-search">Search</label>
      <div class="relative">
        <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
          <svg aria-hidden="true" class="w-4 h-4 text-gray-500 dark:text-gray-400"
               fill="none" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z" stroke="currentColor" stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"/>
          </svg>
        </div>
        <input id="default-search"
               v-model="searchfieldValue"
               class="block w-full p-4 ps-10 pr-[89px] text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 outline-none focus:ring-0"
               placeholder="Search the archive..."
               type="search"
        />
        <button
            class="text-white absolute end-2.5 bottom-2.5 bg-red-800 hover:bg-red-700 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-4 py-2"
            type="submit">
          Search
        </button>
      </div>
    </form>

    <div id="accordion-collapse" class="max-w-[50%] mx-auto mt-7" data-accordion="collapse">
      <h2 id="accordion-collapse-heading-1">
        <button id="accordion-collapse-button" :aria-expanded="collapseOpen"
                aria-controls="accordion-collapse-body-1"
                class="flex items-center justify-between w-full p-5 font-medium border bg-gray-50 rounded-t-xl focus:ring-0"
                data-accordion-target="#accordion-collapse-body-1"
                type="button">
          <span class="text-black font-bold">Advanced Options</span>
          <svg aria-hidden="true" class="w-3 h-3 rotate-180 shrink-0" data-accordion-icon
               fill="none" viewBox="0 0 10 6" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 5 5 1 1 5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"
                  stroke-width="2"/>
          </svg>
        </button>
      </h2>
      <div id="accordion-collapse-body-1" :class="{ 'hidden': !collapseOpen }"
           aria-labelledby="accordion-collapse-heading-1">
        <div id="accordion-collapse-body-content" class="p-5 border border-t-0 bg-white">
          <div>
            <label class="block mb-2 text-sm font-medium text-gray-900" for="orderByKey">Order by Key</label>
            <div class="flex items-center">
              <input id="orderByKey" v-model="orderByKey"
                     class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                     type="text"/>
              <span class="inline-flex material-icons ml-3 cursor-pointer-force select-none items-center"
                    @click="toggleOrderByKeyDirection()">
                      {{ orderByKeyDirection === 'desc' ? 'arrow_downward' : 'arrow_upward' }}
                    </span>
            </div>
          </div>
          <div class="mt-4">
            <label class="flex items-center">
              <input v-model="doNaturalSearch" class="form-checkbox cursor-pointer" type="checkbox">
              <span class="ml-2 text-sm text-gray-900 cursor-pointer">Natural Language Search (Experimental)</span>
            </label>
            <label class="flex items-center">
              <input v-model="excludeForks" class="form-checkbox cursor-pointer" type="checkbox">
              <span class="ml-2 text-sm text-gray-900 cursor-pointer">Exclude forks</span>
            </label>
          </div>
          <div class="mt-4">
            <div class="flex items-center justify-between mb-2">
              <label class="block text-sm font-medium text-gray-900">Comparison</label>
              <button
                  class="text-red-800 cursor-pointer hover:text-red-700 focus:outline-none"
                  type="button"
                  @click="addComparison"
              >
                <span class="material-icons text-sm cursor-pointer-force">add</span>
              </button>
            </div>

            <div v-for="(comparison, index) in comparisons" :key="`comparison-${index}`" class="flex items-center space-x-2 mb-2">
              <input
                  v-model="comparison.key"
                  class="flex-1 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                  placeholder="Key"
                  type="text"
              />

              <select
                  v-model="comparison.operator"
                  class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
              >
                <option value="eq">=</option>
                <option value="gt">&gt;</option>
                <option value="ge">&gt;=</option>
                <option value="lt">&lt;</option>
                <option value="le">&lt;=</option>
              </select>

              <input
                  v-model="comparison.value"
                  class="flex-1 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                  placeholder="Value"
                  type="text"
              />

              <button
                  v-if="comparisons.length > 1"
                  class="text-gray-400 cursor-pointer hover:text-red-600 focus:outline-none"
                  type="button"
                  @click="removeComparison(index)"
              >
                <span class="material-icons text-sm cursor-pointer-force">remove</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>


    <div class="flex justify-center items-center">
      <button class="hover:underline mx-auto mt-3" type="button" @click="toggleSearchInstructions()">
        Instructions
      </button>
    </div>
  </div>


  <div class="min-h-screen w-full bg-gray-100 mt-[80px]">
    <div v-if="isLoading" class="text-center">
      <div class="loader"></div>
    </div>
    <div v-else-if="searchFailed" class="text-center">
      <p class="text-2xl font-bold">Search Failed</p>
      <p class="italic">{{ searchErrMsg }}</p>
      <p class="prose" style="margin: 5px auto auto auto"><a href="https://status.example.com/status/char-archive"
                                                             style="font-size: 11pt;" target="_blank">Status Page</a>
      </p>
    </div>
    <div v-else-if="searchResults.length === 0 && !isLoading && searchfieldValue !== ''" class="text-center">
      <p class="text-2xl font-bold">No results :(</p>
    </div>
    <div v-else class="w-[90%] m-auto">
      <div class="char-list grid-cols-5">
        <li v-for="(card, index) in searchResults" :key="`searchresults-${index}`" :class="resolveCardColor(card)"
            class="char-list-item mt-[10px]">
          <div class="flex flex-col items-center h-full">
            <div class="char-item-grid h-full flex flex-col justify-between">
              <div class="char-list-avatar">
                <a :href="resolveCardLink(card, false)"
                   class="hover:bg-gray-200 bg-gray-200 rounded-lg min-h-[200px]"
                   @click.prevent="clickSearchResult($event, card)"
                >
                  <img :src="resolveCardAvatarURL(card)" class="rounded" onerror="this.src='/img/thumbnail-failure-200.png'">
                </a>
              </div>
              <div class="h-full">
                <p class="char-list-name">
                  <a :href="resolveCardLink(card, false)" @click.prevent="clickSearchResult($event, card)">
                    {{ limitString(card.name, cardNameLengthLimit()) }}
                  </a>
                </p>
                <div class="flex items-center justify-center">
                  <a v-if="card.author != null" :href="resolveCardLink(card, true)"
                     class="char-list-author" @click.prevent="clickSearchResult($event, card)">
                    {{ resolveCardAuthorName(card) }}
                  </a>
                </div>
                <p class="char-list-desc">
                  <a :href="resolveCardLink(card, false)" @click.prevent="clickSearchResult($event, card)">
                    {{ limitString(card.tagline, cardDescLengthLimit()) }}
                  </a>
                </p>
              </div>
            </div>
            <div v-if="card.source !== 'injected'" class="char-list-source-container w-full">
              <div
                  :class="{'grid grid-cols-2 gap-3':card.type === 'lorebook' || (card.chub != null && card.chub.chub_fork)}"
                  class="char-list-source w-full">
                <p v-if="card.type === 'lorebook' || (card.chub != null && card.chub.chub_fork)"
                   class="text-right max-h-[24px]">
                  <Popper :content="`This item is a ${cardResolveIcon(card)[1]}`" arrow hover>
                    <span class="material-icons">{{ cardResolveIcon(card)[0] }}</span>
                  </Popper>
                </p>
                <p :class="{'items-start flex':card.type === 'lorebook' || (card.chub != null && card.chub.chub_fork)}">
                  {{ resolveCardPrettyName(card) }}</p>
              </div>
            </div>
          </div>
        </li>
      </div>

      <nav v-if="searchResults.length > 0 && $route.query.query != null" aria-label="Page navigation" class="my-5">
        <div class="flex flex-col md:flex-row items-center justify-center">
          <div class="mx-auto grid grid-cols-1 grid-rows-2">
            <ul class="list-style-none flex justify-center my-4 select-none">
              <li>
                <router-link
                    :class="currentPage === 1 ? 'pointer-events-none' : 'hover:bg-neutral-100 text-red-primary-hover'"
                    :to="{
                      name: 'Search',
                      query: {
                        query: searchfieldValue ? doubleEncodeUrlParam(searchfieldValue) : undefined,
                        page: currentPage > 2 ? currentPage - 1 : undefined, // Only include if > 1
                        'sort-key': orderByKey && orderByKey !== '' ? orderByKey : undefined,
                        'sort-dir': orderByKey && orderByKey !== '' && orderByKeyDirection !== 'asc' ? orderByKeyDirection : undefined,
                        forks: excludeForks ? 'false' : undefined,
                        natural: doNaturalSearch ? 'true' : undefined,
                        comparison: comparisonParam
                      }
                    }"
                    class="rounded relative block bg-transparent px-3 py-1.5 text-sm text-neutral-600 transition-all duration-300"
                >
                  <button
                      class="px-2 py-1 bg-primary-400 bg-primary-hover text-red-primary font-bold hover:text-white rounded">
                    &larr;
                  </button>
                </router-link>
              </li>
              <li v-for="(page, index) in displayedPages" :key="`pagenumber-${index}-${page}`"
                  class="flex items-center">
                <router-link
                    v-if="typeof page === 'number'"
                    :class="currentPage === page ? 'bg-primary-200 font-medium text-red-primary' : 'bg-transparent text-neutral-600 hover:bg-neutral-100 text-red-primary-hover'"
                    :to="{
                      name: 'Search',
                      query: {
                        query: doubleEncodeUrlParam(searchfieldValue),
                        page: page,
                        'sort-key': orderByKey,
                        'sort-dir': orderByKeyDirection,
                        forks: excludeForks ? 'false' : undefined,
                        natural: doNaturalSearch ? 'true' : undefined,
                        comparison: comparisonParam
                      }
                    }"
                    class="relative block rounded px-3 py-1.5 text-sm transition-all duration-300"
                >{{ page }}
                </router-link>
                <span v-else>...</span>
              </li>
              <li>
                <router-link
                    :class="currentPage === totalPages ? 'pointer-events-none' : 'hover:bg-neutral-100 text-red-primary-hover'"
                    :to="{
                      name: 'Search',
                      query: {
                        query: searchfieldValue ? doubleEncodeUrlParam(searchfieldValue) : undefined,
                        page: currentPage + 1,
                        'sort-key': orderByKey && orderByKey !== '' ? orderByKey : undefined,
                        'sort-dir': orderByKey && orderByKey !== '' && orderByKeyDirection !== 'asc' ? orderByKeyDirection : undefined,
                        forks: excludeForks ? 'false' : undefined,
                        natural: doNaturalSearch ? 'true' : undefined,
                        comparison: comparisonParam
                      }
                    }"
                    class="rounded relative block bg-transparent px-3 py-1.5 text-sm text-neutral-600 transition-all duration-300"
                >
                  <button
                      class="px-2 py-1 bg-primary-400 bg-primary-hover text-red-primary font-bold hover:text-white rounded">
                    &rarr;
                  </button>
                </router-link>
              </li>
            </ul>
            <div class="flex justify-center items-center my-3">
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
                  class="px-2 py-1 bg-primary-400 bg-primary-hover text-red-primary font-bold hover:text-white rounded ml-3"
                  @click="goToPage"
              >
                Go
              </button>
            </div>
          </div>
        </div>
      </nav>
    </div>
  </div>

  <div v-show="showSearchInstructions"
       id="search-instructions-modal"
       class="backdrop-blur-sm h-100 max-h-full overflow-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0"
       tabindex="-1">
    <div class="relative mx-auto mt-20 p-4 w-full h-full">
      <!-- Modal content -->
      <div class="flex flex-col w-[70%] h-[75%] mx-auto bg-white rounded-lg shadow">
        <!-- Modal header -->
        <div class="flex items-center justify-between p-3 border-b rounded-t">
          <h3 class="text-xl font-semibold text-gray-900">
            Search Instructions
          </h3>
          <button
              class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center"
              type="button"
              @click="toggleSearchInstructions()">
            <svg aria-hidden="true" class="w-3 h-3" fill="none" viewBox="0 0 14 14" xmlns="http://www.w3.org/2000/svg">
              <path d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6" stroke="currentColor" stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"/>
            </svg>
            <span class="sr-only">Close modal</span>
          </button>
        </div>
        <!-- Modal body -->
        <div class="flex-grow p-3 space-y-4 overflow-y-scroll">
          <SearchInfo/>
        </div>
        <!-- Modal footer -->
        <div class="flex justify-end items-center p-3 border-t border-gray-200 rounded-b">
          <button
              class="py-2.5 px-5 ms-3 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-red-700 focus:z-10 focus:ring-4 focus:ring-gray-100"
              type="button"
              @click="toggleSearchInstructions()">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
import NavbarRed from "@/components/parts/NavbarRed.vue";
import axios from "axios";
import {convertSnakeCaseToKebabCase, doubleDecodeUrlParam, doubleEncodeUrlParam, limitString} from "@/assets/js/strings";
import {APIHOST, CardDescLengthLimit, CardNameLengthLimit} from "@/components/config"
import {matoPush} from "@/assets/js/mato";
import {injectedFbiCards} from "@/assets/js/intected-fbi";
import SearchInfo from "@/components/parts/SearchInfo.vue";
import Popper from "vue3-popper";
import '@/assets/css/popper.css';
import {initFlowbite} from "flowbite";
import {getRandomItem} from "@/assets/js/array";
import {initializeHandler} from "@/assets/js/source-handler/initialize";
import {mapState} from "vuex";

const SORT_ASC = "asc"
const SORT_DESC = "desc"


export default {
  name: 'SearchResults',
  components: {Popper, SearchInfo, NavbarRed},
  computed: {
    displayedPages() {
      const range = 2 // number of pages to display before and after the current page
      let pages = []
      for (let i = 1; i <= this.totalPages; i++) {
        if (i === 1 || i === this.totalPages || (i >= this.currentPage - range && i <= this.currentPage + range)) {
          pages.push(i)
        } else if (i === this.currentPage - range - 1 || i === this.currentPage + range + 1) {
          pages.push('...')
        }
      }
      return pages
    },
    advancedSearchShouldOpen() {
      // TODO: make sure to add new advanced search items here
      const hasComparison = this.comparisons[0] && this.comparisons[0].key && this.comparisons[0].value
      return (this.orderByKey != null && this.orderByKey !== "") ||
          this.doNaturalSearch === true ||
          this.excludeForks === true ||
          hasComparison
    },
    comparisonParam() {
      const validComparisons = this.comparisons.filter(c => c.key && c.value);
      if (validComparisons.length > 0) {
        const comparisonsArray = validComparisons.map(c => ({
          k: c.key,
          v: c.value,
          c: c.operator
        }));
        return doubleEncodeUrlParam(JSON.stringify(comparisonsArray));
      }
      return undefined;
    },
    ...mapState(["searchKeys"]),
  },
  data() {
    return {
      isLoading: false,
      firstPageLoaded: false,
      searchResults: [],
      searchfieldValue: "",
      isBadSearch: false,
      badSearchStrings: ["sull"], // "child", "toddler", "teen", "year old", "years old", "teenage", "teenager"
      allowedLoliPercent: 1 / 2,
      totalPages: 1,
      currentPage: 1,
      inputPage: null,
      searchResultsCountArg: 20,
      showSearchInstructions: false,
      searchFailed: false,
      searchErrMsg: "",
      orderByKey: "",
      orderByKeyDirection: SORT_ASC,
      excludeForks: false,
      doNaturalSearch: false,
      collapseOpen: false,
      everythingIsLoaded: false,
      comparisons: [{key: '', operator: 'eq', value: ''}]
    }
  },
  methods: {
    doubleEncodeUrlParam,
    cardDescLengthLimit() {
      return CardDescLengthLimit
    },
    toggleSearchInstructions() {
      if (this.showSearchInstructions === false) {
        window.scrollTo(0, 0)
        this.showSearchInstructions = true
        document.getElementsByTagName("body")[0].classList.add("overflow-y-hidden")
        this.$nextTick(() => {
          document.getElementById('search-instructions-modal').scrollTop = 0
        })
        matoPush("UI Click", "Action", "Open search instructions")
      } else {
        this.showSearchInstructions = false
        document.getElementsByTagName("body")[0].classList.remove("overflow-y-hidden")
      }
    },
    cardNameLengthLimit() {
      return CardNameLengthLimit
    },
    cardResolveIcon(card) {
      if (card.chub.chub_fork) {
        return ["call_split", "fork"]
      } else if (card.type === "lorebook") {
        return ["import_contacts", "lorebook"]
      } else {
        console.warn(`Card did not match an icon" ${card}`)
        return ""
      }
    },
    limitString,
    async executeSearch() {
      this.searchFailed = false
      this.searchErrMsg = ""

      // Check if we have either a query OR advanced search options
      const hasAdvancedOptions = (this.orderByKey && this.orderByKey !== "") ||
          this.excludeForks ||
          this.doNaturalSearch ||
          this.comparisons.some(c => c.key && c.value)

      if (!this.searchfieldValue && !hasAdvancedOptions) {
        return
      }

      await this.$nextTick(() => {
        const searchTitle = this.searchfieldValue
            ? `Search - "${this.searchfieldValue}"`
            : "Advanced Search"
        document.title = `Character Card Archive | ${searchTitle}`
      })

      try {
        // Use an empty string if no query is provided
        const parsedQuery = this.parseSearchQuery(this.searchfieldValue || "")
        const stringifiedParsedQueryStr = doubleEncodeUrlParam(parsedQuery)
        const urlParams = new URLSearchParams()

        if (this.orderByKey != null && this.orderByKey !== "") {
          urlParams.append('sort-key', this.orderByKey)
          urlParams.append('sort-dir', this.orderByKeyDirection)
        }

        if (this.excludeForks) {
          urlParams.append('forks', 'false')
        }

        if (this.doNaturalSearch) {
          urlParams.append('natural', 'true')
        }

        const validComparisons = this.comparisons
            .filter(comp => comp.key && comp.value)
            .map(comp => ({
              k: comp.key,
              v: comp.value,
              c: comp.operator
            }))
        if (validComparisons.length > 0) {
          const comparisonsJson = JSON.stringify(validComparisons)
          urlParams.append('comparison', doubleEncodeUrlParam(comparisonsJson))
        }

        let urlParamsString = ""
        if (urlParams.toString()) {
          urlParamsString = "&" + urlParams.toString()
        }

        this.isLoading = true
        const response = await axios.get(
            `${APIHOST}/api/archive/v3/search/query?query=${stringifiedParsedQueryStr}&page=${this.currentPage}&count=${this.searchResultsCountArg}${urlParamsString}`
        )

        // Convert the chub.chub_fullPath key to chub.fullPath
        let obj = response.data.result
        if (obj) {
          for (let i = 0; i < obj.length; i++) {
            if (obj[i].chub && obj[i].chub.chub_fullPath) {
              let fullPathValue = obj[i].chub.chub_fullPath;
              delete obj[i].chub.chub_fullPath;
              obj[i].chub.fullPath = fullPathValue;
            }
          }
        }

        this.searchResults = obj
        this.totalPages = response.data.totalPages

        this.isBadSearch = false
        if (this.searchfieldValue && (this.containsBadStrings(this.searchfieldValue) || response.data.safety.loli >= this.allowedLoliPercent)) {
          const injectCount = this.searchResults.length
          const injectedResults = [];

          for (let i = 0; i < injectCount; i++) {
            if (i < this.searchResults.length) {
              injectedResults.push(this.searchResults[i]);
            }
            injectedResults.push(getRandomItem(injectedFbiCards));
          }

          // Append the remaining search results, if any
          if (injectCount < this.searchResults.length) {
            injectedResults.push(...this.searchResults.slice(injectCount));
          }

          this.searchResults = injectedResults;
          this.isBadSearch = true;
        }

        // Matomo tracking
        if (!this.firstPageLoaded) {
          let searchResultsCount
          if (this.totalPages === 1) {
            searchResultsCount = this.searchResults.length
          } else {
            searchResultsCount = this.searchResultsCountArg * this.totalPages
          }
          if (searchResultsCount == null) {
            console.error("searchResultsCount was null!")
          }
          let orderingStr = ""
          if (this.orderByKey !== "" || this.orderByKeyDirection !== SORT_ASC) {
            orderingStr = ` (${this.orderByKey} ${this.orderByKeyDirection})`
          }
          const searchQuery = this.searchfieldValue || ""
          _paq.push(['setDocumentTitle', document.title])
          _paq.push(['setCustomUrl', `${APIHOST}/#/search?query=${doubleDecodeUrlParam(searchQuery)}${orderingStr}&search_count=${searchResultsCount}`])
          _paq.push(['trackPageView'])
          this.firstPageLoaded = true
        }
      } catch (error) {
        console.error("Failed to search:", error, error.stack)
        this.searchFailed = true
        if (error.response != null) {
          this.searchErrMsg = error.response.data.message
        } else {
          this.searchErrMsg = "Exception"
        }
      }

      this.isLoading = false
    },
    formCardResultLink(result) {
      const handler = initializeHandler(result.source)
      return handler.resolveCardLink(result)
    },
    resolveCardColor(card) {
      const handler = initializeHandler(card.source, card.sourceSpecific, false)
      if (handler == null) {
        console.error(`Failed to initalize handler for source "${card.source}", specific "${card.sourceSpecific}"`)
      } else {
        return handler.cardColor
      }
    },
    resolveCardPrettyName(card) {
      const handler = initializeHandler(card.source, card.sourceSpecific, false)
      if (handler == null) {
        console.error(`Failed to initalize handler for source "${card.source}", specific "${card.sourceSpecific}"`)
      } else {
        return handler.prettyName
      }
    },
    resolveCardAvatarURL(card) {
      const handler = initializeHandler(card.source, card.sourceSpecific, false)
      if (handler == null) {
        console.error(`Failed to initalize handler for source "${card.source}", specific "${card.sourceSpecific}"`)
      } else {
        return handler.resolveCardAvatarURL(card, false, true, 200)
      }
    },
    doSearch() {
      // Check if we have either a query OR advanced search options
      const hasAdvancedOptions = (this.orderByKey && this.orderByKey !== "") ||
          this.excludeForks ||
          this.doNaturalSearch ||
          this.comparisons.some(c => c.key && c.value)

      if (!this.searchfieldValue && !hasAdvancedOptions) {
        // Optionally show a message that either a query or advanced options are required
        return
      }

      if (this.orderByKey == null || this.orderByKey === "") {
        this.removeQueryParameter("sort-key")
        this.removeQueryParameter("sort-dir")
      }

      this.removeQueryParameter("comparison")

      let query = {}

      if (this.searchfieldValue) {
        query.query = doubleEncodeUrlParam(this.searchfieldValue)
      }

      if (this.orderByKey !== "") {
        query['sort-key'] = this.orderByKey
        query['sort-dir'] = this.orderByKeyDirection
      }
      if (this.excludeForks) {
        query.forks = 'false'
      }
      if (this.doNaturalSearch) {
        query.natural = 'true'
      }

      const validComparisons = this.comparisons
          .filter(comp => comp.key && comp.value)
          .map(comp => ({
            k: comp.key,
            v: comp.value,
            c: comp.operator
          }))
      if (validComparisons.length > 0) {
        const comparisonsJson = JSON.stringify(validComparisons)
        query.comparison = doubleEncodeUrlParam(comparisonsJson)
      }

      this.$router.push({query})
    },
    clickSearchResult(event, card) {
      const handler = initializeHandler(card.source, card.sourceSpecific)
      const matoName = handler.generateMatoSearchResult(card.name, card.id, card.author)
      matoPush("UI Click", "Search Results", matoName)

      const href = event.currentTarget.getAttribute('href')

      if (href.startsWith("https://")) {
        // Support injected cards linking to PDF
        window.location = href
      } else {
        // Extract the part after `/#/`
        const path = href.substring(href.indexOf('#/') + 2)
        if (event.ctrlKey || event.metaKey) {
          window.open(window.location.origin + '/#/' + path, '_blank')
        } else {
          this.$router.push(path)
        }
      }
    },
    resolveCardLink(card, isAuthor) {
      if (isAuthor && (card.author == null || card.author === "")) {
        return null
      }
      let url
      if (isAuthor) {
        const handler = initializeHandler(card.source, card.sourceSpecific)
        return handler.resolveCardAuthorLink(card)
      } else {
        url = this.formCardResultLink(card)
      }
      return url
    },
    resolveCardAuthorName(card) {
      const handler = initializeHandler(card.source, card.sourceSpecific)
      const authorName = handler.resolveCardAuthorName(card)
      return limitString(authorName, CardNameLengthLimit)
    },
    containsBadStrings(input) {
      for (let i = 0; i < this.badSearchStrings.length; i++) {
        const regex = new RegExp(`\\b${this.badSearchStrings[i]}\\b`, "gi");
        if (regex.test(input)) {
          return true;
        }
      }
      return false;
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
    goToPage() {
      if (this.inputPage >= 1 && this.inputPage <= this.totalPages) {
        document.activeElement.blur()
        this.currentPage = this.inputPage

        const query = {}

        if (this.$route.query.query) {
          query.query = this.$route.query.query
        }

        query.page = this.inputPage
        query['sort-key'] = this.orderByKey
        query['sort-dir'] = this.orderByKeyDirection

        if (this.excludeForks) {
          query.forks = 'false';
        }

        if (this.doNaturalSearch) {
          query.natural = 'true';
        }

        const validComparisons = this.comparisons
            .filter(comp => comp.key && comp.value)
            .map(comp => ({
              k: comp.key,
              v: comp.value,
              c: comp.operator
            }))
        if (validComparisons.length > 0) {
          const comparisonsJson = JSON.stringify(validComparisons)
          query.comparison = doubleEncodeUrlParam(comparisonsJson)
        }

        if (this.inputPage === 1) {
          delete query.page;
        }

        this.$router.push({query}).catch(err => {
        })

        this.inputPage = null;
      }
    },
    closeOnEscape(event) {
      if (event.key === 'Escape' && this.showSearchInstructions === true) {
        this.toggleSearchInstructions()
      }
    },
    parseSearchQuery(searchString) {
      console.log(`Search Query: \`${searchString}\`. Natural: ${this.doNaturalSearch}. Exclude forks: ${this.excludeForks}.`);
      return searchString;
    },
    toggleOrderByKeyDirection() {
      if (this.orderByKeyDirection === SORT_ASC) {
        this.orderByKeyDirection = SORT_DESC
      } else {
        this.orderByKeyDirection = SORT_ASC
      }
    },
    hasQueryChanged(newVal, oldVal, query) {
      return oldVal && newVal[query] !== oldVal[query];
    },
    addComparison() {
      this.comparisons.push({key: '', operator: 'eq', value: ''});
    },
    removeComparison(index) {
      if (this.comparisons.length > 1) {
        this.comparisons.splice(index, 1);
      }
    }
  },
  async mounted() {
    window.addEventListener('keyup', this.closeOnEscape)
    await this.$nextTick(() => {
      initFlowbite()
    })

    if (Object.keys(this.searchKeys).length === 0) {
      try {
        const keysResponse = await axios.get(`${APIHOST}/api/archive/v1/search/keys`)
        this.$store.commit('searchKeys', keysResponse.data)
      } catch (e) {
        this.searchFailed = true
        this.searchErrMsg = "Exception"
        console.error(e)
      }
    }

    this.everythingIsLoaded = true // Indicate that searchKeys are loaded
  },
  beforeDestroy() {
    window.removeEventListener('keyup', this.closeOnEscape);
  },
  beforeRouteEnter(to, from, next) {
    next(async vm => {
      // Convert query args like `sort_dir` to `sort-dir`.
      const convertedQuery = convertSnakeCaseToKebabCase(vm.$route.query)
      await vm.$router.replace({query: convertedQuery})

      if (!vm.$route.query.query) {
        document.title = "Character Card Archive | Search"
      }

      // Set searchfieldValue to empty string if no query parameter
      vm.searchfieldValue = vm.$route.query.query
          ? doubleDecodeUrlParam(vm.$route.query.query)
          : ""

      if (vm.$route.query['sort-key'] != null && vm.$route.query['sort-key'] !== "") {
        vm.orderByKey = vm.$route.query['sort-key']
      }
      if (vm.$route.query['sort-dir'] != null && vm.$route.query['sort-dir'] !== "") {
        vm.orderByKeyDirection = vm.$route.query['sort-dir']
      }
      if (vm.$route.query.forks != null && vm.$route.query.forks !== "") {
        vm.excludeForks = vm.$route.query.forks === "false"
      }
      if (vm.$route.query.natural != null && vm.$route.query.natural !== "") {
        vm.doNaturalSearch = vm.$route.query.natural === "true"
      }

      if (vm.$route.query.comparison) {
        try {
          const decodedComparisons = doubleDecodeUrlParam(vm.$route.query.comparison)
          const comparisonsArray = JSON.parse(decodedComparisons)
          vm.comparisons = comparisonsArray.map(comp => ({
            key: comp.k,
            operator: comp.c,
            value: comp.v
          }))
        } catch (e) {
          console.error('Failed to parse comparisons:', e)
          vm.comparisons = [{key: '', operator: 'eq', value: ''}]
        }
      }

      vm.collapseOpen = vm.advancedSearchShouldOpen
    });
  },
  beforeRouteLeave() {
    // TODO: make sure to add new advanced search options here.
    this.searchfieldValue = this.orderByKey = ""
    this.orderByKeyDirection = SORT_ASC
    this.excludeForks = false
    this.doNaturalSearch = false
    this.comparisons = [{key: '', operator: 'eq', value: ''}]
    this.showSearchInstructions = false
    document.getElementsByTagName("body")[0].classList.remove("overflow-y-hidden")
  },
  watch: {
    '$route.query': {
      immediate: true,
      handler: async function (newVal, oldVal) {
        if (!this.everythingIsLoaded) {
          // Wait until searchKeys are loaded
          await new Promise(resolve => {
            const unwatch = this.$watch('everythingIsLoaded', (newReady) => {
              if (newReady) {
                unwatch()
                resolve()
              }
            })
          })
        }

        const {query: newQuery, page: newPage, 'sort-key': sort_key, 'sort-dir': sort_dir, forks, natural} = newVal
        const {query: oldQuery, page: oldPage} = oldVal || {}

        // Get comparison separately to handle undefined
        const newComparison = newVal ? newVal.comparison : undefined
        const oldComparison = oldVal ? oldVal.comparison : undefined

        // Handle query change
        if (newQuery !== oldQuery) {
          this.searchfieldValue = newQuery ? doubleDecodeUrlParam(newQuery) : ""
          this.searchResults = []
          this.firstPageLoaded = false
          this.currentPage = 1 // always reset the page back to 1.
        }

        // Handle page change
        if (newPage !== oldPage) {
          this.currentPage = newPage ? parseInt(newPage) : 1
          this.inputPage = null

          if (this.searchResults.length > 0) {
            if (this.totalPages > 0 && newPage > this.totalPages) {
              console.log(`Refusing request because we've already loaded all the pagination. Requested page: ${newPage}. Total pages: ${this.totalPages}.`)
              this.currentPage = this.totalPages
              this.removeQueryParameter("page")
            } else {
              matoPush("Search Results", "Change Page", this.currentPage)
            }
          }
        }

        const sortKeyChanged = this.hasQueryChanged(newVal, oldVal, 'sort-key')
        const sortDirChanged = this.hasQueryChanged(newVal, oldVal, 'sort-dir')
        const forksChanged = this.hasQueryChanged(newVal, oldVal, 'forks')
        const naturalChanged = this.hasQueryChanged(newVal, oldVal, 'natural')
        const comparisonChanged = newComparison !== oldComparison

        if (comparisonChanged) {
          this.searchResults = []
          if (newComparison) {
            try {
              const decodedComparisons = doubleDecodeUrlParam(newComparison)
              const comparisonsArray = JSON.parse(decodedComparisons)
              this.comparisons = comparisonsArray.map(comp => ({
                key: comp.k,
                operator: comp.c,
                value: comp.v
              }))
            } catch (e) {
              console.error('Failed to parse comparisons:', e)
              this.comparisons = [{key: '', operator: 'eq', value: ''}]
            }
          } else {
            this.comparisons = [{key: '', operator: 'eq', value: ''}]
          }
        }

        if (sortKeyChanged || sortDirChanged || forksChanged || naturalChanged) {
          this.searchResults = []
          this.orderByKey = sort_key || ""
          this.orderByKeyDirection = sort_dir || SORT_ASC

          this.excludeForks = forks === 'false' // `excludeForks` is true when `forks=false`
          this.doNaturalSearch = natural === 'true'
        }

        window.scrollTo(0, 0)
        await this.executeSearch()
      }
    }
  }
}
</script>

<style scoped>
@import '@/assets/css/char-list.css';
@import '@/assets/css/archive.css';
@import '@/assets/css/loader.css';
@import '@/assets/css/search.css';

#default-search::placeholder {
  text-align: left;
}

input {
  text-align: left;
}

a {
  cursor: pointer;
}

#accordion-collapse-button, #accordion-collapse-body-content {
  border-color: var(--main-red);
}

@media (max-width: 564px) {
  .search-results-lore-icon {
    @apply col-start-2 col-end-3 justify-self-center;
  }

}
</style>
