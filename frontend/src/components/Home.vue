<template>
  <FilebrowserTop/>
  <div
      class="min-h-screen w-full max-md:p-4 md:p-8 flex items-center max-md:text-2xl md:text-lg max-md:justify-center bg-gray-100 absolute top-0 mt-[60px]">
    <ArchiveHome/>
  </div>
  <Alerts/>
</template>

<script>

import FilebrowserTop from "@/components/parts/NavbarRed.vue";
import ArchiveHome from "@/components/parts/archive/ArchiveHome.vue";
import Alerts from "@/components/parts/Alerts.vue";


export default {
  components: {Alerts, ArchiveHome, FilebrowserTop},
  data() {
    return {}
  },
  beforeRouteEnter(to, from, next) {
    next(vm => {
      document.title = "Character Card Archive"
      _paq.push(['setDocumentTitle', document.title])
      _paq.push(['setCustomUrl', window.location.href])
      _paq.push(['trackPageView'])
    })
  },
};
</script>

<style scoped>
@import '@/assets/css/front.css';
</style>