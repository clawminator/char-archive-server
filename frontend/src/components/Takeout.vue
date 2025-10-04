<template>
  <NavbarRed/>

  <div class="container container-override mx-auto px-1 lg:px-8 pb-4 mt-[80px]">
    <div class="text-white text-center py-5 mb-6 rounded-lg shadow-lg bg-navy-blue-light">
      <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold">Data Takeout</h1>
    </div>
    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <div class="text-black">
        <p>
          For centuries, philosophers have debated the question of who archives an archive? Finally, an answer has been
          found: you do!
        </p>
      </div>
    </div>
    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">Special Downloads</h2>
      <div class="text-black">
        <p>
          <a href="https://char-archive.example.com/api/archive/v1/aicg-chronicles?url=https://rentry.org/aicg_chronicles/raw&render=true"
             target="_blank">https://rentry.org/aicg_chronicles</a>
        </p>
        <p>
          <a href="https://char-archive.example.com/api/archive/v1/aicg-chronicles?url=https://rentry.org/aicg_chronicles-NASA/raw&render=true"
             target="_blank">https://rentry.org/aicg_chronicles-NASA</a>
        </p>
        <p>
          <a href="https://char-archive.example.com/api/archive/v1/aicg-chronicles?url=https://rentry.org/aicg_chronicles-NARA/raw&render=true"
             target="_blank">https://rentry.org/aicg_chronicles-NARA</a>
        </p>
        <!--        <p>-->
        <!--          No special downloads. Please use the torrents instead.-->
        <!--        </p>-->
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">Torrents</h2>
      <div class="text-black">
        <p>
          Torrents are provided and are incremental, meaning you need all the torrents for the complete archive.
          I do not seed these torrents past their initial upload, so hopefully someone is still seeding them.
        </p>
        <p>
          Torrents and their READMEs are available in <a href="/#/files?path=/takeout">/takeout</a> folder.
        </p>
        <p>
          Want to joint the waiting list? <a href="https://forms.example.com/form/dl8zmcd3">Submit your email here.</a>
        </p>
      </div>
    </div>

  </div>
</template>

<script>
import NavbarRed from "@/components/parts/NavbarRed.vue";

export default {
  name: 'Info',
  components: {NavbarRed},
  data() {
    return {}
  },
  mounted() {
  },
  beforeDestroy() {
  },
  beforeRouteEnter(to, from, next) {
    next(vm => {
      document.title = "Character Card Archive | Data Takeout"
      _paq.push(['setDocumentTitle', document.title])
      _paq.push(['setCustomUrl', window.location.href])
      _paq.push(['trackPageView'])
    })
  },
  beforeRouteLeave() {
  },
}
</script>

<style scoped>
.jumbo {
  background-color: var(--main-red);
}

.prose {
  min-width: 100%;
}
</style>
