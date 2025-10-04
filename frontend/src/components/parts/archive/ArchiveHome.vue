<template>
  <div class="w-full h-full">
    <div class="flex flex-col items-center justify-center mb-5">
      <h1 class="text-4xl lg:text-7xl font-extrabold text-center md:mb-7 mt-8">Character Archive</h1>
      <div class="text-center">
        <p id="charCount" class="min-h-[28px] mb-3 text-base md:text-xl"></p>
        <p id="plapCost" class="min-h-[28px] mb-3 text-base md:text-xl"></p>
      </div>

      <div class="my-10 w-full md:w-[50%]">
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
                   class="block w-full p-4 ps-10 pr-[89px] text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-0 outline-none"
                   placeholder="Search the archive..." required
                   type="search"
            />
            <button
                class="text-white absolute end-2.5 bottom-2.5 bg-red-800 hover:bg-red-700 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-4 py-2"
                type="submit">
              Search
            </button>
          </div>
        </form>
        <div class="flex justify-center items-center">
          <a class="hover:underline mx-auto mt-3 prose text-sm hover:bg-[unset]" href="/#/search">
            Advanced
          </a>
        </div>
      </div>

      <div class="text-lg p-4 sm:p-6 md:p-6 prose mb-6 w-[75%]">
        <div class="text-center">
          The Character Archive collects character cards from across the internet. This is a repository that serves
          as a sanctuary for characters of all kinds, preserving their unique characteristics. Our mission
          is to safeguard these cherished characters.
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6 w-[75%]">
        <div class="text-black text-center">
          <a href="/#/tags" class="hover:bg-[unset]">Tags</a><br>
<!--          <a href="/#/card-ideas" class="hover:bg-[unset]">Slop Generator</a>-->
        </div>
      </div>

      <h1 class="text-4xl font-extrabold text-center mb-7 mt-8">Random Characters</h1>
      <div class="flex flex-col items-center justify-center">
        <button :disabled="isFetchingRandomChars"
                class="bg-red-800 hover:bg-red-700 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded"
                @click="fetchRandomCards">
          Regenerate
        </button>
        <div class="mt-2">
          <input id="toggleImages" v-model="showImages" type="checkbox">
          <label for="toggleImages"> Show Images (NSFW)</label>
        </div>
      </div>
    </div>

    <div class="char-list">
      <li v-for="card in randomChars" :key="`randomchar-${card.id}`"
          :class="resolveCardColor(card)" class="char-list-item">
        <div class="flex flex-col items-center h-full">
          <div class="char-item-grid h-full flex flex-col justify-between">
            <div class="char-list-avatar">
              <a :class="{'animate-pulse' : card.placeholder !== undefined}" :href="resolveCardLink(card)"
                 class="hover:bg-gray-200 bg-gray-200 rounded-lg w-[200px]">
                <img v-if="card.placeholder === undefined" :src="resolveCardAvatarURL(card, showImages)" alt=""
                     class="rounded" onerror="this.src='/img/thumbnail-failure-200.png'">
              </a>
            </div>
            <div class="h-full">
              <p class="char-list-name">
              <span v-if="card.placeholder != null"
                    class="inline-block w-[50%] min-h-[1em] bg-gray-200 animate-pulse"></span>
                <a v-else :href="resolveCardLink(card)">
                  {{ limitString(card.name, CardNameLengthLimit()) }}
                </a>
              </p>
              <div class="flex items-center justify-center">
                <a v-if="card.author != null"
                   :href="resolveCardAuthor(card)"
                   class="char-list-author">
                  {{ limitString(card.author, CardNameLengthLimit()) }}
                </a>
              </div>
              <p class="char-list-desc">
                <a v-if="card.tagline != null" :href="resolveCardLink(card)">
                  {{ limitString(card.tagline, CardDescLengthLimit()) }}
                </a>
              </p>
            </div>
          </div>
          <div class="char-list-source-container w-full">
            <p class="char-list-source w-full">
              {{ resolveCardPrettyName(card) }}
            </p>
          </div>
        </div>
      </li>
    </div>

    <div class="text-center w-full">
      <a class="italic hover:bg-[unset] underline hover:underline text-black pt-3 block" href="/#/ultra-random">Ultra Random</a>
    </div>


    <h1 class="text-4xl font-extrabold text-center mb-7 mt-20">Latest Characters</h1>
    <div class="char-list">
      <li v-for="card in latestChars" :key="`randomchar-${card.id}`"
          :class="resolveCardColor(card)" class="char-list-item">
        <div class="flex flex-col items-center h-full">
          <div class="char-item-grid h-full flex flex-col justify-between">
            <div class="char-list-avatar">
              <a :class="{'animate-pulse' : card.placeholder !== undefined}" :href="resolveCardLink(card)"
                 class="hover:bg-gray-200 bg-gray-200 rounded-lg w-[200px]">
                <img v-if="card.placeholder === undefined" :src="resolveCardAvatarURL(card, showImages)" alt=""
                     class="rounded" onerror="this.src='/img/thumbnail-failure-200.png'">
              </a>
            </div>
            <div class="h-full">
              <p class="char-list-name">
              <span v-if="card.placeholder != null"
                    class="inline-block w-[50%] min-h-[1em] bg-gray-200 animate-pulse"></span>
                <a v-else :href="resolveCardLink(card)">
                  {{ limitString(card.name, CardNameLengthLimit()) }}
                </a>
              </p>
              <div class="flex items-center justify-center">
                <a v-if="card.author != null"
                   :href="resolveCardAuthor(card)"
                   class="char-list-author">
                  {{ limitString(card.author, CardNameLengthLimit()) }}
                </a>
              </div>
              <div class="char-list-desc">
                <div v-if="card.placeholder == null" class="text-center font-bold mb-3">
                  {{ DateTime.fromISO(card.added).toLocaleString(DateTime.DATETIME_MED) }}
                </div>
                <a v-if="card.tagline != null" :href="resolveCardLink(card)">
                  {{ limitString(card.tagline, CardDescLengthLimit()) }}
                </a>
              </div>
            </div>
          </div>
          <div class="char-list-source-container w-full">
            <p class="char-list-source w-full">
              {{ resolveCardPrettyName(card) }}
            </p>
          </div>
        </div>
      </li>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import {matoPush} from "@/assets/js/mato";
import {doubleEncodeUrlParam, limitString} from "@/assets/js/strings";
import {DateTime} from "luxon";
import {generatePlaceholderCards} from "@/assets/js/card.js"
import {resolveCardAuthor, resolveCardAvatarURL, resolveCardColor, resolveCardLink, resolveCardPrettyName} from "@/assets/js/char-list";
import {CardDescLengthLimit, CardNameLengthLimit} from "../../config";
import {APIHOST} from "@/components/config"


export default {
  name: 'ArchiveHome',
  data() {
    return {
      isFetchingRandomChars: false,
      randomChars: [],
      latestChars: [],
      showImages: false,
      healthCheckInterval: null,
      initalRandomLoaded: false,
      searchfieldValue: '',
      archiveInfo: {},
    }
  },
  computed: {
    DateTime() {
      return DateTime
    },
  },
  methods: {
    CardDescLengthLimit() {
      return CardDescLengthLimit
    },
    CardNameLengthLimit() {
      return CardNameLengthLimit
    },
    resolveCardPrettyName,
    resolveCardAuthor,
    resolveCardAvatarURL,
    resolveCardLink,
    resolveCardColor,
    limitString,
    async fetchRandomCards() {
      this.isFetchingRandomChars = true
      let response
      try {
        response = await axios.get(`${APIHOST}/api/archive/v1/random-character?count=5`)
        this.randomChars = response.data
        if (!this.initalRandomLoaded) {
          this.initalRandomLoaded = true
        } else {
          matoPush('User Interface', 'Click', 'Regenerate random chars');
        }
      } catch (err) {
        if (err.response != null && err.response.status === 429) {
          console.warn("429 error on random chars")
        } else {
          console.error(err)
        }
      }
      setTimeout(() => {
        // Cooldown
        this.isFetchingRandomChars = false
      }, 600)
    },
    async fetchLatestCards() {
      let response
      try {
        response = await axios.get(`${APIHOST}/api/archive/v1/latest-character?count=5`)
      } catch (err) {
        console.error(err)
      }
      if (response != null) {
        this.latestChars = response.data
      }
    },
    async fetchInfo() {
      const response = await axios.get(`${APIHOST}/api/archive/v1/info`)
      this.archiveInfo = response.data
      const charCount = this.archiveInfo.booru.characters + this.archiveInfo.chub.characters + this.archiveInfo.generic.characters + this.archiveInfo.nyaime.characters
      document.getElementById("charCount").innerHTML = `Serving ${charCount.toLocaleString()} characters.`

      const plapData = this.archiveInfo.plap_costs
      const plapCost = Math.round(plapData.calculated * plapData.base_adj * plapData.drago_adj)
      document.getElementById("plapCost").innerHTML = `${plapCost.toLocaleString('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      })} spent.`
    },
    doSearch() {
      this.$router.push({
        path: 'search',
        query: {query: doubleEncodeUrlParam(this.searchfieldValue)}
      })
    },
  },
  async created() {
    this.randomChars = generatePlaceholderCards()
    this.latestChars = generatePlaceholderCards()
    await this.fetchInfo()
    await this.fetchRandomCards()
    await this.fetchLatestCards()
  },
  async mounted() {
    // await this.$nextTick(() => {
    //   initFlowbite()
    //   initTE({Collapse, Ripple})
    // })
  }
}
</script>

<style scoped>
/* @import '@/assets/css/home.css'; is empty */
@import '@/assets/css/char-list.css';
@import '@/assets/css/colors.css';
@import '@/assets/css/search.css';
</style>
