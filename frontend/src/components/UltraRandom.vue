<template>
  <NavbarRed/>
  <div class="container container-override mx-auto px-1 lg:px-8 pb-4 mt-[80px]">
    <div class="text-white text-center py-5 mb-6 rounded-lg shadow-lg bg-navy-blue-light">
      <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold">Ultra Random</h1>
    </div>
    <div id="textContent" ref="textContent" class="text-center font-bold"></div>
    <div ref="loader" class="w-full">
      <div class="flex flex-col items-center justify-center mb-5">
        <div class="loader my-10"></div>
      </div>
    </div>
    <div ref="randomList">
      <div class="flex flex-col items-center mb-3">
        <div class="flex items-center">
          <button :disabled="isCooldown"
                  class="regen-button bg-red-800 hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-red-800 text-white font-bold py-2 px-4 rounded"
                  @click="fetchRandomCards">
            Regenerate
          </button>
          <p ref="cooldownText" class="ml-2"></p>
        </div>
        <div class="my-4">
          <input ref="tagInput"
                 v-model="tagInput"
                 class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                 placeholder="Enter comma-separated tags"
                 type="text"
                 @keyup.enter="!isCooldown && fetchRandomCards()">
        </div>
        <p>Press SPACE to refresh.</p>
      </div>
      <div class="char-list" style="width:100%!important">
        <li v-for="card in items" :key="`randomchar-${card.id}`"
            :class="resolveCardColor(card)" class="char-list-item mb-3">
          <div class="flex flex-col items-center h-full">
            <div class="char-item-grid h-full flex flex-col justify-between">
              <div class="char-list-avatar">
                <a :class="{'animate-pulse' : card.placeholder !== undefined}" :href="resolveCardLink(card)"
                   class="hover:bg-gray-200 bg-gray-200 rounded-lg w-[200px]">
                  <img v-if="card.placeholder === undefined" :src="resolveCardAvatarURL(card, true)" alt=""
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
      <p ref="slopText" class="text-center">mmmm... yummy slop...</p>
    </div>
  </div>
</template>

<script>
import NavbarRed from "@/components/parts/NavbarRed.vue";
import axios from "axios";
import {APIHOST, CardDescLengthLimit, CardNameLengthLimit} from "@/components/config";
import {resolveCardAuthor, resolveCardAvatarURL, resolveCardColor, resolveCardLink, resolveCardPrettyName} from "@/assets/js/char-list";
import {doubleEncodeUrlParam, limitString} from "@/assets/js/strings";
import axiosRetry from "axios-retry";
import {matoPush} from "@/assets/js/mato";

export default {
  name: 'UltraRandom',
  components: {NavbarRed},
  data() {
    return {
      items: [],
      isCooldown: false,
      tagInput: '',
    }
  },
  methods: {
    resolveCardAvatarURL,
    resolveCardColor,
    resolveCardAuthor,
    CardNameLengthLimit() {
      return CardNameLengthLimit
    },
    CardDescLengthLimit() {
      return CardDescLengthLimit
    }, resolveCardLink, limitString, resolveCardPrettyName,
    async fetchRandomCards() {
      // If the cooldown is active, don't execute the function
      if (this.isCooldown) {
        return;
      }

      // Re-add the listener since there may be issues with typing and whatever
      document.removeEventListener('keypress', this.handleKeyPress)
      document.addEventListener('keypress', this.handleKeyPress)

      this.isCooldown = true;

      this.$refs.textContent.innerHTML = "";
      this.$refs.loader.hidden = false;
      this.$refs.randomList.hidden = true;

      try {
        const tags = this.tagInput.split(',').map(tag => tag.trim()).filter(tag => tag !== '');
        const tagsParam = tags.length > 0 ? `?tags=${doubleEncodeUrlParam(tags.join(','))}` : '';
        let response = await axios.get(`${APIHOST}/api/archive/v1/random-character-ultra${tagsParam}`);
        this.items = response.data;
        matoPush('User Interface', 'Click', 'Regenerate ultra random chars');
      } catch (e) {
        this.$refs.randomList.hidden = true;
        this.$refs.textContent.innerHTML = "Exception";
        console.error(e);
      }

      this.$refs.loader.hidden = true;
      this.$refs.randomList.hidden = false;
      this.$refs.cooldownText.style.visibility = "visible";

      let countdown = 6;
      this.$refs.cooldownText.innerHTML = countdown;

      const countdownInterval = setInterval(() => {
        countdown--;
        this.$refs.cooldownText.innerHTML = countdown;

        if (countdown === 0) {
          clearInterval(countdownInterval);
          this.isCooldown = false;
          this.$refs.cooldownText.style.visibility = "hidden";
        }
      }, 1000);
    },
    handleKeyPress(event) {
      if (event.code === 'Space' && document.activeElement !== this.$refs.tagInput) {
        event.preventDefault();
        this.fetchRandomCards();
      }
    },
  },
  created() {
  },
  async mounted() {
    axiosRetry(axios, {
      retries: 3, // Number of retries
      retryDelay: (retryCount) => {
        return retryCount * 5000; // Delay for 5 seconds (5000 milliseconds) on each retry
      },
      retryCondition: (error) => {
        return error.response.status === 429; // Retry only if the status code is 429
      },
    });
    window.scrollTo(0, 0)
    await this.fetchRandomCards()
  },
  beforeRouteEnter(to, from, next) {
    next(vm => {
      document.title = "Character Card Archive | Ultra Random";
      _paq.push(['setCustomUrl', window.location.href])
      _paq.push(['setDocumentTitle', document.title])
      _paq.push(['trackPageView'])
      document.addEventListener('keypress', vm.handleKeyPress)
    })
  },
  beforeRouteLeave(to, from, next) {
    document.removeEventListener('keypress', this.handleKeyPress)
    next();
  },
}
</script>

<style scoped>
@import '@/assets/css/char-list.css';
@import '@/assets/css/colors.css';
@import '@/assets/css/loader.css';
</style>
