<template>
  <div class="char-card-grid lg:w-full m-[10px] grid">
    <div class="char-card-left flex flex-col self-start items-start mx-6 mb-10 md:mx-auto">
      <img
          id="avatarImage"
          :src="avatarSrc"
          :style="{ width: avatarWidth + 'px', height: avatarHeight + 'px' }"
          alt=""
          class="avatar-image items-center justify-center rounded-lg shadow-lg bg-white mx-auto"
          @error="handleImageError"
      >
      <div class="flex flex-col items-center mt-3 mx-auto">
        <div class="flex">
          <Popper v-if="cardData.type === 'character'" arrow content="V2 PNG card" hover>
            <button
                id="cardV2DlButtonEl"
                class="card-v2-dl-button mx-2 w-36 h-10 inline-flex justify-center items-center rounded-md text-sm font-semibold text-white shadow-lg"
                @click="showDlButtonConfirmation($event, downloadCardPNG)">
              <span class="material-icons cursor-pointer-force">download</span>
              <span class="font-extrabold text-lg force-h-16">PNG</span>
            </button>
          </Popper>
          <Popper :content="`JSON ${cardData.type === 'character' ? 'card' : 'lorebook'}`" arrow hover>
            <button
                id="cardJsonDlButtonEl"
                class="bg-green-800 mx-2 w-36 h-10 inline-flex justify-center items-center rounded-md text-sm font-semibold text-white shadow-lg disabled:bg-green-600 disabled:cursor-not-allowed"
                @click="showDlButtonConfirmation($event, downloadCardJSON)">
              <span class="material-icons cursor-pointer-force">data_object</span>
              <span class="font-extrabold text-lg force-h-16">&nbsp;JSON</span>
            </button>
          </Popper>
        </div>
        <div class="flex">
          <Popper v-if="cardData.type === 'character'" arrow content="Copy SillyTavern Import URL" hover>
            <button
                id="stCopyButtonEl"
                class="bg-gray-800 mt-3 mx-2 w-36 h-10 inline-flex justify-center items-center rounded-md text-sm font-semibold text-white shadow-lg disabled:bg-gray-600 disabled:cursor-not-allowed"
                @click="showDlButtonConfirmation($event, cardPngUrlToClipboard)">
              <img class="h-[80%] inline" src="/img/sites/sillytavern-logo-white.png">
              <span class="font-extrabold text-md force-h-16">&nbsp;Copy URL</span>
            </button>
          </Popper>
          <Popper v-if="cardData.type === 'character'" arrow content="Send to a third-party service" hover>
            <button
                id="thirdPartySendButtonEl"
                class="bg-gray-600 mt-3 mx-3 w-36 h-10 inline-flex justify-center items-center rounded-md text-sm font-semibold text-white shadow-lg disabled:bg-gray-500 disabled:cursor-not-allowed"
                @click="toggleImportModal()">
              <span class="material-icons cursor-pointer-force">cloud_upload</span>
              <span class="font-extrabold text-lg force-h-16">&nbsp;Send</span>
            </button>
          </Popper>
        </div>
      </div>
    </div>
    <div class="char-card-right">
      <div :class="handler.cardColor"
           class="rounded-lg shadow-lg prose p-4 justify-between items-center w-full max-w-full mb-6 flex flex-col sm:flex-row">
        <h2 class="m-0 flex items-center text-xl">
          {{ cardData.name }}&nbsp;&nbsp;
          <Popper v-if="handler.hasExternal"
                  :content="`View on ${handler.prettyName}`"
                  arrow hover>
            <a :href="resolveCardExternalUrl()"
               class="hover:bg-[unset]"
               target="_blank">
              <span class="material-icons cursor-pointer-force">open_in_new</span>
            </a>
          </Popper>
        </h2>
        <div class="text-center mt-2 sm:mt-0">
          <Popper :content="`This item is a ${cardData.type}`" arrow hover>
            <span class="material-icons">{{ cardData.type === 'character' ? "person" : "import_contacts" }}</span>
          </Popper>
          <Popper arrow content="This item is a fork" hover>
            <span v-if="checkCardForked(cardData)" class="material-icons ml-3">call_split</span>
          </Popper>
        </div>
        <div class="text-right mt-2 sm:mt-0">
          <a :href="handler.resolveCardAuthorLink(cardData)"
             class="whitespace-nowrap font-bold">
            {{ resolveCardAuthorName(cardData) }}</a>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-lg p-4 prose mb-6 max-w-full">
        <div class="italic font-bold mb-6">{{
            cardData.tagline !== "" ? cardData.tagline : cardData.creatorNotes
          }}
        </div>
        <div class="prose max-w-full" v-html="parseUntrustedHTML(cardData.description)"></div>
        <p v-if="cardData.source === 'generic' || cardData.source === 'booru' || cardData.source === 'webring' "
           class="text-xs italic">auto-generated
          description</p>
      </div>
      <div class="bg-white rounded-lg shadow-lg p-4 prose mb-6 max-w-full">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-xl sm:text-2xl md:text-2xl font-bold max-w-full truncate m-0">Node Info</h2>
          <Popper arrow content="Download node JSON" hover>
            <span class="material-icons cursor-pointer-force"
                  @click="downloadCardNode()">download</span>
          </Popper>
        </div>
        <table class="table-auto">
          <tbody>
          <tr v-if="handler.hasDownloads">
            <td class="font-bold pr-3">Downloads</td>
            <td>{{ cardData.node[handler.getDownloadKey] }}</td>
          </tr>
          <tr v-if="cardData.source === 'chub'">
            <td class="font-bold pr-3">chub.ai Stats</td>
            <td>
              <Popper :content="[
                                  cardData.node.n_favorites ? `${cardData.node.n_favorites} favorites` : '',
                                  cardData.type === 'character' && cardData.node.nChats ? `${cardData.node.nChats} chats` : '',
                                  cardData.type === 'character' && cardData.node.nMessages ? `${cardData.node.nMessages} messages` : ''
                                ].filter(Boolean).join(', ')"
                      arrow
                      hover>
                <div>
                  <span v-if="cardData.node.n_favorites != null" class="mr-6 inline-flex items-center"><HeartOutlined/>&nbsp;{{ cardData.node.n_favorites }}</span>
                  <span v-if="cardData.type === 'character' && cardData.node.nChats != null" class="mr-5 inline-flex items-center"><BookOutlined/>&nbsp;{{ cardData.node.nChats }}</span>
                  <span v-if="cardData.type === 'character' && cardData.node.nMessages != null" class="inline-flex items-center"><MessageOutlined/>&nbsp;{{ cardData.node.nMessages }}</span>
                </div>
              </Popper>
            </td>
          </tr>
          <tr>
            <td class="font-bold align-middle pr-3">Tags</td>
            <td v-if="cardData.source === 'chub'">{{ cardData.node.topics.join(", ") }}</td>
            <td v-else>{{ cardData.tags.join(", ") }}</td>
          </tr>
          <tr>
            <td class="font-bold whitespace-nowrap pr-3">Token Estimate</td>
            <td>{{ cardData.metadata.totalTokens }}</td>
          </tr>
          <tr v-if="checkCardForked(cardData)">
            <td class="font-bold pr-3">Forked From</td>
            <td>
              <a :href="`/#/chub/${cardData.chub.forked.source[0]}/${cardData.type}/${cardData.chub.forked.source[1]}`">
                {{ `${cardData.chub.forked.source[0]}/${cardData.chub.forked.source[1]}` }}
              </a>
            </td>
          </tr>
          <tr v-if="cardData.source === 'chub'">
            <td class="font-bold pr-3">Created On</td>
            <td>{{ isoToStr(cardData.node.createdAt) }}
              <span v-if="isoToStr(cardData.node.createdAt) !== isoToStr(cardData.node.lastActivityAt)">
                &nbsp;(last updated on {{ isoToStr(cardData.node.lastActivityAt) }})
              </span>
            </td>
          </tr>
          <tr v-if="cardData.metadata.created != null">
            <td class="font-bold pr-3">Created On</td>
            <td v-if="DateTime.fromISO(cardData.metadata.created).toMillis() !== 0">
              {{ isoToStr(cardData.metadata.created) }}
            </td>
            <td v-else>-</td>
          </tr>
          <tr>
            <td class="font-bold pr-3">Archive Added</td>
            <td>{{ isoToStr(cardData.added) }}</td>
          </tr>
          <tr v-if="(cardData.source === 'chub' || cardData.source === 'nyaime') && isoToStr(cardData.updated) !== isoToStr(cardData.added)">
            <td class="font-bold pr-3">Archive Refreshed</td>
            <td>{{ isoToStr(cardData.updated) }}</td>
          </tr>
          <tr>
            <td class="font-bold pr-3">Source</td>
            <td v-if="cardData.source === 'generic'">{{ capitalizeFirstLetter(cardData.sourceSpecific) }}</td>
            <td v-else>{{ handler.prettyName }}</td>
          </tr>
          <tr v-if="cardData.source === 'generic'">
            <td class="font-bold pr-3">Source URL</td>
            <td v-if="cardData.metadata.source_url != null">
              {{ cardData.metadata.source_url }}
            </td>
            <td v-else>-</td>
          </tr>
          </tbody>
        </table>
      </div>
      <div v-if="handler.hasComments"
           class="bg-white rounded-lg shadow-lg p-4 prose mb-6 max-w-full">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-xl sm:text-2xl md:text-2xl font-bold max-w-full truncate m-0">Comments</h2>
          <Popper arrow content="Download ratings" hover>
            <span class="material-icons cursor-pointer-force"
                  @click="downloadRatings()">download</span>
          </Popper>
        </div>
        <div class="max-h-52 overflow-auto">
          <table class="table-auto">
            <tbody>
            <tr v-for="rating in this.cardData.ratings" v-if="this.cardData.ratings.length !== 0"
                :key="`rating-${rating.id}`">
              <td v-if="handler.hasRatings" class="min-w-10">{{
                  (rating.rating !== null) ? `${rating.rating} ⭐` : "&nbsp;&nbsp;&nbsp;-"
                }}
              </td>
              <td class="italic w-[75%]">{{
                  (rating.comment && rating.comment.length > 0) ? rating.comment : "User did not leave a comment."
                }}
              </td>
              <td class="w-[25%] text-center">{{ isoToStr(rating.created) }}</td>
            </tr>
            <tr v-else>
              <td class="w-[75%]">No comments</td>
              <td class="w-[25%] text-center">-</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-if="cardData.source === 'chub' && cardData.type === 'character'"
           class="bg-white rounded-lg shadow-lg p-4 prose mb-6 max-w-full">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-xl sm:text-2xl md:text-2xl font-bold max-w-full truncate m-0">Chats</h2>
          <Popper arrow content="Download chats" hover>
            <span class="material-icons cursor-pointer-force" @click="downloadChats()">download</span>
          </Popper>
        </div>
        <div class="max-h-52 overflow-auto">
          <table class="table-auto">
            <thead>
            <tr>
              <th class="text-left">Date</th>
              <th class="text-center">Number of Messages</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="chat in this.cardData.chats" v-if="this.cardData.chats.length !== 0"
                :key="`chat-${chat.id}`">
              <td class="w-[75%]">{{ isoToStr(chat.created) }}</td>
              <td class="text-center w-[25%]">{{ chat.count }}</td>
            </tr>
            <tr v-else>
              <td>No chats</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="cardData.source === 'chub' && cardData.chub.forks.forks.length > 0"
           class=" bg-white max-w-full mb-6 p-4 prose rounded-lg shadow-lg">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-xl sm:text-2xl md:text-2xl font-bold max-w-full truncate m-0">Forks</h2>
        </div>
        <div class="max-h-52 overflow-auto">
          <table class="table-auto">
            <tbody>
            <tr v-for="fork in cardData.chub.forks.forks" :key="`fork-${fork}`">
              <td>
                <a :href="`/#/chub/${fork[0]}/${cardData.type}/${fork[1]}`">
                  {{ `${fork[0]}/${fork[1]}` }}
                </a>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="handler.hasVersions"
           class="bg-white rounded-lg shadow-lg p-4 prose mb-6 max-w-full">
        <h2 class="text-xl sm:text-2xl md:text-2xl font-bold mb-2">Versions</h2>
        <p class="mb-0">
          Different versions may be a result of internal API modifications and not necessarily due to changes in
          the card definition.
        </p>
        <div class="max-h-52 overflow-auto">
          <table class="table-auto">
            <tbody>
            <tr v-for="(item, index) in Object.values(cardData.versions)" :key="`version-${index}`">
              <td class="w-[75%]">{{ isoToStr(item) }}{{ index === 0 ? " (current version)" : "" }}</td>
              <td class="text-center w-[25%]">
                <span class="material-icons cursor-pointer-force" @click="downloadVersion(index)">download</span>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow-lg p-4 prose mb-6 max-w-full">
        <h2 class="text-xl sm:text-2xl md:text-2xl font-bold mb-2">Actions</h2>
        <a class="cursor-pointer" @click="downloadCardOriginal()">Download unmodified original card</a><br>
        <a :href="resolveDefinitionLink()" target="_blank">View card definition</a>
      </div>
    </div>
  </div>

  <div v-show="showImportModal"
       id="import-modal"
       class="backdrop-blur-sm h-100 max-h-full overflow-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0"
       tabindex="-1">
    <div class="relative mx-auto mt-20 p-4 w-full h-full">
      <!-- Modal content -->
      <div
          class="flex flex-col w-full sm:w-[80%] md:w-[70%] lg:w-[60%] xl:w-[50%] min-h-[400px] h-[80%] sm:h-[70%] md:h-[60%] lg:h-[50%] xl:h-[40%] mx-auto bg-white rounded-lg shadow">
        <!-- Modal header -->
        <div class="flex items-center justify-between p-3 border-b rounded-t">
          <h3 class="text-xl font-semibold text-gray-900">
            Send to Third-Party Service
          </h3>
          <button
              class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center"
              type="button"
              @click="toggleImportModal()">
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
          <button
              class="card-v2-dl-button mx-auto w-32 h-10 inline-flex justify-center items-center rounded-md py-1 px-2 text-sm font-semibold text-white shadow-lg mr-3"
              style="background-color: #1f4439" @click="sendToCharluv()">
            <img src="/img/sites/charluv-logo.png">
          </button>
          <button
              class="card-v2-dl-button mx-auto w-40 h-10 inline-flex justify-center items-center rounded-md py-1 px-2 text-sm font-semibold text-white shadow-lg"
              style="background-color: #337ab7" @click="sendToKobold()">
            <img class="h-5 mr-3" src="/img/sites/koboldai-logo-icon.png">
            KoboldAI Lite
          </button>
        </div>
        <!-- Legal disclaimer -->
        <div class="p-3 text-sm italic text-center text-gray-500 border-t border-gray-200">
          Connection to third-party services is provided for the convenience of the user and does not
          constitute an endorsement. Use at your own risk.
        </div>
        <!-- Modal footer -->
        <div class="flex justify-end items-center p-3 border-t border-gray-200 rounded-b">
          <button
              class="py-2.5 px-5 ms-3 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-red-900 focus:z-10 focus:ring-4 focus:ring-gray-100"
              type="button"
              @click="toggleImportModal()">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from "vuex";
import {APIHOST} from "@/components/config";
import {saveAs} from "file-saver";
import {Collapse, initTE, Ripple} from "tw-elements";
import {initFlowbite} from "flowbite";
import Popper from "vue3-popper";
import '@/assets/css/popper.css';
import {DateTime} from "luxon";
import {matoPush, matoPushDl} from "@/assets/js/mato";
import {capitalizeFirstLetter, doubleEncodeUrlParam, limitString, parseUntrustedHTML} from "@/assets/js/strings";
import {checkCardForked} from "@/assets/js/card";
import SearchInfo from "@/components/parts/SearchInfo.vue";
import {initializeHandler} from "@/assets/js/source-handler/initialize";
import {BookOutlined, HeartOutlined, MessageOutlined} from '@ant-design/icons-vue';

export default {
  name: 'ArchiveItem',
  computed: {
    DateTime() {
      return DateTime
    },
    handler() {
      return initializeHandler(this.cardData.source, this.cardData.sourceSpecific)
    },
    ...mapState(["cardData", "cardSource"]),
  },
  components: {
    SearchInfo,
    Popper,
    HeartOutlined,
    BookOutlined,
    MessageOutlined
  },
  data() {
    return {
      showImportModal: false,
      avatarSrc: '',
      avatarWidth: 0,
      avatarHeight: 0,
    }
  },
  methods: {
    parseUntrustedHTML,
    limitString,
    doubleEncodeUrlParam,
    checkCardForked,
    capitalizeFirstLetter,
    isoToStr(iso) {
      return DateTime.fromISO(iso).toLocaleString(DateTime.DATETIME_MED)
    },
    thumbnailSize(width, height, maxSize) {
      let scalingFactor = Math.min(maxSize / width, maxSize / height)
      let newWidth = Math.round(width * scalingFactor)
      let newHeight = Math.round(height * scalingFactor)
      return [newWidth, newHeight]
    },
    setAvatarURL() {
      if (!this.cardData.image) {
        this.setFailureImage();
        return;
      }

      const {width, height} = this.cardData.image;
      if (width && height) {
        const [newWidth, newHeight] = this.thumbnailSize(width, height, 400);
        this.avatarWidth = newWidth;
        this.avatarHeight = newHeight;
        this.avatarSrc = this.handler.resolveCardAvatarURL(this.cardData, false, false, 400, true);
      } else {
        this.setFailureImage();
      }
    },
    setFailureImage() {
      this.avatarWidth = 400;
      this.avatarHeight = 400;
      this.avatarSrc = '/img/thumbnail-failure-400.png';
      document.getElementById("cardV2DlButtonEl").disabled = true;
      // document.getElementById("cardJsonDlButtonEl").disabled = true; // Don't disable the raw def download since it's not an image
      document.getElementById("stCopyButtonEl").disabled = true;
      document.getElementById("thirdPartySendButtonEl").disabled = true;
    },
    handleImageError() {
      this.avatarSrc = '/img/thumbnail-failure-400.png';
    },
    generateCardPNGUrl() {
      const [urlEnd, filename] = this.handler.resolveDataDownload(this.cardData)
      return `${APIHOST}/api/archive/v1/${this.cardSource}/image/${this.cardData.type}/${urlEnd}?definition=true`
    },
    copyToClipboard(text) {
      navigator.clipboard.writeText(text)
    },
    cardPngUrlToClipboard() {
      this.copyToClipboard(this.generateCardPNGUrl())
      matoPush("UI Click", "Action", "Copy ST import URL")
    },
    async downloadCardPNG() {
      const [urlEnd, filename] = this.handler.resolveDataDownload(this.cardData)
      const url = this.generateCardPNGUrl()
      matoPushDl(url)
      await this.downloadFile(url, filename + ".card.png")
    },
    downloadFile(url, filename) {
      // A download function that allows us to track the completion.
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("GET", url, true);
        xhr.responseType = "blob";

        xhr.onload = function () {
          if (xhr.status === 200) {
            const blob = xhr.response;
            const link = document.createElement("a");
            link.href = window.URL.createObjectURL(blob);
            link.download = filename;
            link.click();
            resolve();
          } else {
            reject(new Error("Download failed"));
          }
        };

        xhr.onerror = function () {
          reject(new Error("Download failed"));
        };

        xhr.send();
      });
    },
    resolveCardDlType() {
      if (this.cardData.type === "character") {
        return "card"
      } else if (this.cardData.type === "lorebook") {
        return "lorebook"
      } else {
        throw new Error()
      }
    },
    resolveCardAuthorName(card) {
      const authorName = this.handler.resolveCardAuthorName(card)
      return limitString(authorName, 100)
    },
    async downloadCardJSON() {
      const [urlEnd, filename] = this.handler.resolveDataDownload(this.cardData)
      const url = `${APIHOST}/api/archive/v1/${this.cardSource}/def/${this.cardData.type}/${urlEnd}`
      await this.downloadFile(url, `${filename}.${this.resolveCardDlType()}.json`)
      matoPushDl(url)
    },
    downloadCardOriginal() {
      const [urlEnd, filename] = this.handler.resolveDataDownload(this.cardData)
      const url = `${APIHOST}/api/archive/v1/${this.cardSource}/def/${this.cardData.type}/${urlEnd}?unmodified=true`
      saveAs(url, `${filename}.${this.resolveCardDlType()}.original.json`)
      matoPushDl(url)
    },
    downloadCardNode() {
      const [urlEnd, filename] = this.handler.resolveDataDownload(this.cardData)
      const url = `${APIHOST}/api/archive/v1/${this.cardData.source}/node/${this.cardData.type}/${urlEnd}` // ?node=true
      saveAs(url, filename + ".node.json")
      matoPushDl(url)
    },
    downloadChats() {
      const [urlEnd, filename] = this.handler.resolveDataDownload(this.cardData)
      const url = `${APIHOST}/api/archive/v1/chub/chats/${urlEnd}`
      saveAs(url, `${filename}.chats.json`);
      matoPushDl(url)
    },
    downloadRatings() {
      const [urlEnd, filename] = this.handler.resolveDataDownload(this.cardData)
      const url = `${APIHOST}/api/archive/v1/${this.cardData.source}/ratings/${this.cardData.type}/${urlEnd}`
      saveAs(url, filename + ".ratings.json")
      matoPushDl(url)
    },
    downloadVersion(version) {
      let [urlEnd, filename] = this.handler.resolveDataDownload(this.cardData);
      const apiUrl = new URL(`${APIHOST}/api/archive/v1/${this.cardData.source}/image/${this.cardData.type}/${urlEnd}`);
      const searchParams = new URLSearchParams();
      searchParams.append('definition', 'true');

      if (version != null) {
        const humanVersion = Object.values(this.cardData.versions).length - version;
        searchParams.append('version', version);
        filename = `${filename} -- version ${humanVersion}`;
      }

      apiUrl.search = searchParams.toString();
      saveAs(apiUrl.toString(), `${filename}.card.json`);
      matoPushDl(apiUrl.toString());
    },
    resolveDefinitionLink() {
      const [urlEnd, filename] = this.handler.resolveDataDownload(this.cardData)
      return `/#/definition?source=${this.cardData.source}&type=${this.cardData.type}&path=${doubleEncodeUrlParam(urlEnd)}`

    },
    async showDlButtonConfirmation(event, action) {
      const button = event.currentTarget
      const originalInnerHTML = button.innerHTML
      const checkmarkElement = document.createElement('span')
      checkmarkElement.className = 'material-icons animate-spin'
      checkmarkElement.textContent = 'refresh'

      button.innerHTML = ''
      button.appendChild(checkmarkElement)

      try {
        await action()
        checkmarkElement.className = 'material-icons'
        checkmarkElement.textContent = 'check_circle'
      } catch (error) {
        console.error("Error downloading file:", error)
        checkmarkElement.className = 'material-icons'
        checkmarkElement.textContent = 'cancel'
      }

      await new Promise(r => setTimeout(r, 1000))

      button.removeChild(checkmarkElement)
      button.innerHTML = originalInnerHTML
    },
    toggleImportModal() {
      if (this.showImportModal === false) {
        window.scrollTo(0, 0)
        this.showImportModal = true
        document.getElementsByTagName("body")[0].classList.add("overflow-hidden")
        this.$nextTick(() => {
          document.getElementById('import-modal').scrollTop = 0
        })
        matoPush("UI Click", "Action", "Open import modal")
      } else {
        this.showImportModal = false
        document.getElementsByTagName("body")[0].classList.remove("overflow-hidden")
      }
    },
    closeOnEscape(event) {
      if (event.key === 'Escape' && this.showImportModal === true) {
        this.toggleImportModal()
      }
    },
    resolveCardExternalUrl() {
      try {
        return this.handler.resolveCardExternalUrl(this.cardData)
      } catch (e) {
        console.error(e)
      }
    },
    sendToCharluv() {
      const url = `https://charluv.com/character/create?import=${encodeURIComponent(this.generateCardPNGUrl())}`
      matoPush("UI Click", "Action", "Send to Charluv")
      matoPushDl(url)
      window.open(url, "_blank").focus()
    },
    sendToKobold() {
      const url = `https://lite.koboldai.net/?carc=${this.generateCardPNGUrl()}`
      matoPush("UI Click", "Action", "Send to KobolAI Lite")
      matoPushDl(url)
      window.open(url, "_blank").focus()
    }
  },
  mounted() {
    window.addEventListener('keyup', this.closeOnEscape);
    this.showImportModal = false
    document.title = `Character Card Archive | ${this.handler.pageName(this.cardData)}`
    this.setAvatarURL()

    this.$nextTick(() => {
      initFlowbite()
      initTE({Collapse, Ripple})
    })
  },
  beforeUnmount() {
    document.body.classList.remove("overflow-hidden")
    window.removeEventListener('keyup', this.closeOnEscape)
  },
  beforeDestroy() {
    window.removeEventListener('keyup', this.closeOnEscape)
  },
  watch: {}
};
</script>

<style scoped>
@import '@/assets/css/char-card.css';
@import '@/assets/css/archive.css';
@import '@/assets/css/colors.css';
</style>
