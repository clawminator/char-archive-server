<template>
  <NavbarRed/>
  <div class="container container-override mx-auto px-1 lg:px-8 pb-4 mt-[80px]">
    <div class="text-white text-center py-5 mb-6 rounded-lg shadow-lg bg-navy-blue-light">
      <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold">Slop Generator</h1>
    </div>

    <div id="textContent" ref="textContent" class="text-center font-bold"></div>

    <div class="flex flex-col items-center mb-6">
      <div class="flex items-center">
        <button :disabled="isCooldown"
                class="regen-button bg-red-800 hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-red-800 text-white font-bold py-2 px-4 rounded"
                @click="fetchCardIdea">
          Regenerate
        </button>
        <p ref="cooldownText" class="ml-2"></p>
      </div>
    </div>

    <div class="max-w-4xl mx-auto space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Character Name</label>
        <input :value="isLoading ? loadingText : (cardIdea ? cardIdea.name : '')"
               class="w-full px-4 py-3 border border-gray-300 rounded-md bg-gray-50 text-gray-800 cursor-not-allowed"
               readonly
               type="text">
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
        <textarea :value="isLoading ? '' : (cardIdea ? cardIdea.description : '')"
                  class="w-full px-4 py-3 border border-gray-300 rounded-md bg-gray-50 text-gray-800 cursor-not-allowed resize-none"
                  readonly
                  rows="15">
        </textarea>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Opening Message</label>
        <textarea :value="isLoading ? '' : (cardIdea ? cardIdea.openingMessage : '')"
                  class="w-full px-4 py-3 border border-gray-300 rounded-md bg-gray-50 text-gray-800 cursor-not-allowed resize-none"
                  readonly
                  rows="15">
        </textarea>
      </div>

      <!-- Citations Section -->
      <div class="mt-8">
        <label class="block text-sm font-medium text-gray-700 mb-2">Citations</label>
        <div class="bg-gray-50 border border-gray-300 rounded-md p-4">
          <div v-for="(citation, index) in cardIdea.citations" v-if="cardIdea && cardIdea.citations && cardIdea.citations.length > 0" :key="index" class="mb-2 last:mb-0">
            <div class="flex items-center text-sm">
              <span class="font-medium text-gray-600">{{ index + 1 }}.</span>
              <a :href="formCardResultLink(citation)"
                 class="ml-2 text-blue-600 hover:text-blue-800 hover:underline"
                 rel="noopener noreferrer"
                 target="_blank">
                {{ citation.id }}
              </a>
              <span class="ml-2 text-gray-500">({{ citation.source }})</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavbarRed from "@/components/parts/NavbarRed.vue";
import axios from "axios";
import {APIHOST} from "@/components/config";
import axiosRetry from "axios-retry";

export default {
  name: 'CardIdeas',
  components: {NavbarRed},
  data() {
    return {
      cardIdea: null,
      isCooldown: false,
      isLoading: false,
      loadingText: 'Generating',
      dotCount: 0,
      loadingInterval: null,
    }
  },
  methods: {
    startLoadingAnimation() {
      this.dotCount = 0;
      this.loadingText = 'Generating';
      this.loadingInterval = setInterval(() => {
        this.dotCount = (this.dotCount + 1) % 4;
        this.loadingText = 'Generating' + '.'.repeat(this.dotCount);
      }, 500);
    },
    stopLoadingAnimation() {
      if (this.loadingInterval) {
        clearInterval(this.loadingInterval);
        this.loadingInterval = null;
      }
    },
    formCardResultLink(citation) {
      let id = citation.id
      if (citation.source === "chub") {
        id = "character/" + citation.id.split("/")[1]
      }
      return `/#/${citation.source}/${citation.author}/${id}`;
    },
    async fetchCardIdea() {
      // If the cooldown is active, don't execute the function
      if (this.isCooldown) {
        return;
      }

      this.isCooldown = true;
      this.isLoading = true;
      this.startLoadingAnimation();
      this.$refs.textContent.innerHTML = "";
      this.cardIdea = null

      try {
        let response = await axios.get(`${APIHOST}/api/archive/v1/card-ideas`);
        this.cardIdea = response.data;
        _paq.push(['trackEvent', 'User Interface', 'Click', 'Regenerate card idea']);
      } catch (e) {
        this.cardIdea = {
          "name": "Error loading card idea. Please try again.",
          "description": null,
          "openingMessage": null,
          "citations": null
        }
        console.error(e);
      }

      this.isLoading = false;
      this.stopLoadingAnimation();
      this.$refs.cooldownText.style.visibility = "visible";

      let countdown = 5;
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
        return error.response && error.response.status === 429; // Retry only if the status code is 429
      },
    });
    window.scrollTo(0, 0)
    await this.fetchCardIdea()
  },
  beforeRouteEnter(to, from, next) {
    next(vm => {
      document.title = "Character Card Archive | Card Ideas";
      _paq.push(['setCustomUrl', window.location.href])
      _paq.push(['setDocumentTitle', document.title])
      _paq.push(['trackPageView'])
    })
  },
  beforeRouteLeave(to, from, next) {
    this.stopLoadingAnimation();
    next();
  },
  beforeDestroy() {
    this.stopLoadingAnimation();
  }
}
</script>

<style scoped>
@import '@/assets/css/char-list.css';
@import '@/assets/css/colors.css';
@import '@/assets/css/loader.css';
</style>
