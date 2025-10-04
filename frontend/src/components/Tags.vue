<template>
  <NavbarRed/>
  <div class="mx-auto px-1 lg:px-8 pb-4 mt-[80px] overflow-x-hidden w-full">
    <!-- Header Section -->
    <div class="text-white text-center py-5 mb-6 rounded-lg shadow-lg bg-navy-blue-light">
      <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold">Tags</h1>
    </div>

    <!-- Content Container -->
    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 mb-6 w-full">
      <!-- Search Bar -->
      <div class="mb-4">
        <input
            v-model="searchQuery"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Search tags..."
            type="text"
        />
      </div>

      <!-- Tags Count -->
      <div :class="{ 'invisible': items[0][1] === '' }" class="text-center">
        {{ items.length.toLocaleString() }} Tags
      </div>

      <!-- Instruction -->
      <div class="text-center italic mb-4">Click a column name to sort it.</div>

      <!-- Table Header -->
      <div class="flex bg-gray-50 rounded-t-lg">
        <!-- Tag Column Header -->
        <div
            class="flex-1 px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer flex items-center"
            @click="sort('tag')"
        >
          Tag
          <span v-if="sortKey === 'tag'">
            <span
                v-if="sortDesc"
                class="material-icons ml-1 select-none"
            >
              arrow_drop_down
            </span>
            <span v-else class="material-icons ml-1 select-none">
              arrow_drop_up
            </span>
          </span>
        </div>

        <!-- Count Column Header -->
        <div
            class="flex-1 px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer flex items-center"
            @click="sort('count')"
        >
          Count
          <span v-if="sortKey === 'count'">
            <span
                v-if="sortDesc"
                class="material-icons ml-1 select-none"
            >
              arrow_drop_down
            </span>
            <span v-else class="material-icons ml-1 select-none">
              arrow_drop_up
            </span>
          </span>
        </div>
      </div>

      <!-- Scroller -->
      <RecycleScroller
          :item-size="ROW_HEIGHT"
          :items="sortedItems"
          class="mt-1 block w-full h-[1000px] overflow-auto"
          key-field="0"
      >
        <template #default="{ item, index }">
          <div
              :key="index"
              :class="index % 2 === 1 ? 'bg-gray-100' : ''"
              class="flex border-b border-gray-200"
          >
            <!-- Tag Column -->
            <div class="flex-1 px-4 py-4">
              <div class="text-sm text-gray-900">
                <a
                    v-if="item[1] !== ''"
                    :href="`/#/search?query=tags:&quot;${doubleEncodeUrlParam(item[0])}&quot;`"
                    class="underline hover:underline text-black hover:bg-transparent"
                >
                  {{ item[0] }}
                </a>
                <span v-else>{{ item[0] }}</span>
              </div>
            </div>

            <!-- Count Column -->
            <div class="flex-1 px-4 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ item[1] }}</div>
            </div>
          </div>
        </template>
      </RecycleScroller>
    </div>
  </div>
</template>

<script>
import NavbarRed from "@/components/parts/NavbarRed.vue";
import {doubleEncodeUrlParam} from "@/assets/js/strings";
import {APIHOST} from "@/components/config";
import {RecycleScroller} from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';

export default {
  name: 'Info',
  components: {NavbarRed, RecycleScroller},
  data() {
    return {
      items: [["Loading...", ""]],
      sortKey: '',
      sortDesc: false,
      ROW_HEIGHT: 50,
      searchQuery: '',
    };
  },
  computed: {
    sortedItems() {
      const sortKey = this.sortKey;
      const sortDesc = this.sortDesc;
      const searchQuery = this.searchQuery.toLowerCase();

      let filteredItems = [...this.items];

      // Filter items based on the search query
      if (searchQuery) {
        filteredItems = filteredItems.filter(item => {
          return item[0].toLowerCase().includes(searchQuery);
        });
      }

      // Sort the filtered items
      if (sortKey) {
        filteredItems.sort((a, b) => {
          let aValue = sortKey === 'tag' ? a[0].toLowerCase() : Number(a[1]);
          let bValue = sortKey === 'tag' ? b[0].toLowerCase() : Number(b[1]);

          if (aValue < bValue) return sortDesc ? 1 : -1;
          if (aValue > bValue) return sortDesc ? -1 : 1;
          return 0;
        });
      }

      return filteredItems;
    },
  },
  methods: {
    doubleEncodeUrlParam,
    sort(key) {
      if (this.sortKey === key) {
        this.sortDesc = !this.sortDesc;
      } else {
        this.sortKey = key;
        this.sortDesc = false;
      }
      // No need to manually set this.items; computed property handles sorting
    },
  },
  async created() {
    if (this.items.length > 1) {
      return;
    }
    try {
      const response = await fetch(`${APIHOST}/api/archive/v2/search/tags`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      this.items = await response.json();
    } catch (error) {
      console.log(error);
      this.items = [["Error...", ""]];
    }
  },
  mounted() {
    // Any additional mounted logic if needed
  },
  beforeRouteEnter(to, from, next) {
    next(vm => {
      document.title = "Character Card Archive | Tags";
      _paq.push(['setCustomUrl', window.location.href]);
      _paq.push(['setDocumentTitle', document.title]);
      _paq.push(['trackPageView']);
    });
  },
  beforeRouteLeave() {
    // Any cleanup before leaving the route if needed
  },
};
</script>

<style scoped>
/* Removed most custom styles in favor of Tailwind utility classes */

/* If you have custom colors like bg-navy-blue-light, ensure they are defined in your Tailwind config */

</style>
