<template>
  <NavbarRed/>
  <Filebrowser/>
</template>

<script>
// TODO: expire alert popup

import NavbarRed from "@/components/parts/NavbarRed.vue";
import Filebrowser from "@/components/parts/filebrowser/browser.vue";


export default {
  components: {NavbarRed, Filebrowser},
  data() {
    return {}
  },
  // beforeRouteEnter(to, from, next) {
  //   next(vm => {
  //   });
  // },
  // beforeRouteUpdate(to, from, next) {
  //   next();
  // },
};
</script>

<style scoped>
</style>