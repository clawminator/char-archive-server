<template>
  <NavbarRed/>
  <div class="container container-override mx-auto px-1 lg:px-8 pb-4 mt-[80px]">
    <div class="text-white text-center py-5 mb-6 rounded-lg shadow-lg bg-navy-blue-light">
      <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold">About</h1>
    </div>
    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <div class="text-black">
        <p>
          Chatbots powered by artificial intelligence have been around for decades, but only recently have they become
          capable of engaging in human-like interactivity. Following the release of OpenAI's GPT-3.5 in March of 2022,
          creative
          individuals discovered that the AI could take on "personalities" and role-play as a character. A community
          formed around chatting with these "bots" and sharing the "character cards" that defined a personality.
          Concerned
          about the capabilities of the AI and the creativity of the users, the corporations that owned the AI models
          took steps to restrict this activity, claiming it was "out of scope" and "unsafe".
        </p>
        <p>
          The Character Archive was created to protect this creativity.
        </p>
        <p>
          <strong><a href="https://status.example.com/status/char-archive" target="_blank">Status Page</a></strong>
        </p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">Searching</h2>
      <div class="text-black">
        <p>
          A very powerful search is provided.
          <span class="font-bold">Nearly every part of a card and lorebook is indexed</span>,
          making it easy to narrow your searches down to exactly what you want. The search is unified, so throw an
          author or a site name in. Or just type a few words from a card you barely remember.
        </p>
        <p>
          Detailed search instructions are available on the search page. Click the "Instructions" link.
        </p>
      </div>
    </div>


    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">The Archive</h2>
      <div class="text-black">
        <p>
          Character and lorebook avatars are shrunk to a maximum of 1000 px by 1000 px and the resulting PNG files are
          compressed.
        </p>
        <p>
          Character definitions are normalized to the spec V2 format and lorebooks are normalized to standardize their
          data. The original, unmodified definitions are stored alongside these reformatted versions and are available
          for download.
        </p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">chub.ai</h2>
      <div class="text-black">
        <p>
          Archive and mirror of <a href="https://characterhub.org" target="_blank">chub.ai</a>.
        </p>
        <p>
          Characters and lorebooks are scraped from chub.ai every hour or so. A complete scrape is performed at least
          once a month.
        </p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">booru.plus</h2>
      <div class="text-black">
        <p>
          Character cards scraped from (the now-defunct) <span class="font-mono">booru.plus/+pygmalion</span>. Comments
          were also scraped as well.
        </p>
        <p>
          The final scrape of booru.plus was on March 4, 2024 and the site went down sometime in late March or early
          April of that year. Consequently, this is not a complete archive and an unknown amount of data is missing.
        </p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">RisuAI RisuRealm</h2>
      <div class="text-black">
        <p>
          Character cards from <span class="font-mono">realm.risuai.net</span> are scraped daily. User info is not
          scraped. Cards are in the V3 format.
        </p>
        <p>RisuRealm has an awful API that serves incorrect data. The scraper tries its best to parse it but an unknwon
          number of cards fail and are skipped.</p>
        <p>The JSON from CCv3 (CharX) cards is extracted and the rest of the CharX is discarded, meaning the embedded assets are not stored.</p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">Character Tavern</h2>
      <div class="text-black">
        <p>
          Character cards scraped <span class="font-mono">character-tavern.com</span>. Comments are scraped.
        </p>
        <p>
          There was an incompatibility with the image conversion program used by the scraper that resulted in corrupted card avatars for this site. It was fixed mid-August 2025.
        </p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">Webring</h2>
      <div class="text-black">
        <p>
          Archive of the Neocities <a href="https://chatbots.neocities.org/" target="_blank">AI chatbot webring</a>. CCv3 cards are skipped.
        </p>
<!--        <p>-->
<!--          Site owners can opt out via the-->
<!--          <span class="font-mono">&#60;meta name="chub-archive-exclude" content="true"&#62;</span> HTML tag.-->
<!--        </p>-->
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">Alternative Bot Websites</h2>
      <div class="text-black">
        <p>Various bot-posting websites.</p>
        <p>
          <span class="font-mono">nyai.me</span>&nbsp;&nbsp;Bot catalog with chan-like features. Associated with 4chan. CCv3 cards are skipped.
        </p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">Generic Character Cards</h2>
      <div class="text-black">
        <p>
          The scrapers crawl the web searching for character cards. One primary source are files stored on <span
            class="font-mono">catbox.moe</span>
        </p>
        <p>
          If a chub.ai author is found in a card's metadata, it is added to the chub.ai archive.
        </p>

        <h2 class="text-lg font-bold mt-8">Imported Data Sources</h2>
        <p>
          <span class="font-bold">Janitor AI:</span> 69k cards scraped from Janitor AI before they made card
          definitions private. This is an incomplete archive. A larger archive exists on <a
            href="https://huggingface.co/datasets/AUTOMATIC/jaicards" target="_blank">Huggingface</a> that contains 190k
          cards. Although this larger archive will not be integrated into the Character Archive because JanitorAI cards are
          consistently low-quality, it has been included in our takeout torrents under the <span class="font-mono">/third-party</span>
          folder.
        </p>
        <p>
          <span class="font-bold">Pygmalion Discord Server:</span> this has not been imported into the archive and
          only exists in the <a href="/#/files?path=/third-party/Pygmalion+Discord+Server+04-18-2023">file
          browser</a>. Contains cards from the Pygmalion Discord server up to 04-18-2023.
        </p>
        <p>
          <span class="font-bold">Roko's Basilisk:</span> scrape of Roko's Basilisk, an early but influental frontend
          for chatbots which shut down after a week over concerns regarding OpenAI's terms of service. Contains the
          defs of many CAI bots that remain private on character.ai. Predates chub.ai and SillyTavern. Authors,
          where found, have been imported.
        </p>
        <p>
          <span class="font-bold">VenusAI:</span> VenusAI up to 05-27-2023, scraped by Koreans.
        </p>
        <p>
          <span class="font-bold">VenusAI Official Discord Server:</span> cards from the official VenusAI Discord.
          This archive was created on 05-28-2023 and originally distributed as <span class="font-mono">ai_characters_archive.zip</span>.
        </p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">Historical</h2>
      <div class="text-black">
        <p>
          Original archives from third-parties are available in the <a href="/#/files?path=/historical">file
          browser</a>. These are stored for historical reasons and most have been integrated into the generic character
          archive.
        </p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">Logs</h2>
      <div class="text-black">
        <p>
          Logs from various proxies are available in the <a href="/#/files?path=/logs">file browser</a>.
        </p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-2xl font-bold mb-2">Other</h2>
      <div class="text-black">
        <p>
          Miscellaneous data relating to chatbots and this archive is available in the <a
            href="/#/files?path=/other">file browser</a>.
        </p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-4 sm:p-6 md:p-6 prose mb-6">
      <h2 class="text-xl sm:text-2xl md:text-2xl font-bold mb-2">Contact</h2>
      Found some bad shit that the scrapers accidentally archived? Send me a message.
      <div class="text-black">
        <p>
          Matrix: <a href="https://matrix.to/#/@example:example.com">@example:example.com</a>
          <br>
          Email: <a href="mailto:contact@example.com">contact@example.com</a>
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
  created() {
  },
  mounted() {
  },
  beforeRouteEnter(to, from, next) {
    next(vm => {
      document.title = "Character Card Archive | About";
      _paq.push(['setCustomUrl', window.location.href])
      _paq.push(['setDocumentTitle', document.title])
      _paq.push(['trackPageView'])
    })
  },
  beforeRouteLeave() {
  },
}
</script>

<style scoped>
.prose {
  min-width: 100%;
}
</style>
