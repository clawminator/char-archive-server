<template>
  <div class="m-3">
    <div class="prose mb-3">
      <h2 id="cardName" class="ml-12">
        <span class="font-bold">{{ cardSourceStr }}</span>{{ cardName }}
      </h2>
    </div>

    <div class="fields-container mx-12">
      <div
          v-for="field in orderedFields"
          :key="field.key"
          class="field-box border-2 border-black p-2 rounded mb-4"
      >
        <h3 class="font-semibold mb-2">{{ toTitleCase(field.key.replaceAll("_", " ")) }}</h3>
        <div class="field-content">
          <pre><code v-html="(field.content == null ? 'None' : field.content)"></code></pre>
        </div>
      </div>
    </div>
    <div class="flex flex-col items-center justify-center">
      <a :href="apiDefUrl">View Raw Definition</a>
    </div>
  </div>
</template>

<script>
import hljs from 'highlight.js'
import {doubleDecodeUrlParam, toTitleCase} from "@/assets/js/strings";
import 'highlight.js/styles/atom-one-light.min.css'
import {APIHOST} from "@/components/config";
import {initializeHandler} from "@/assets/js/source-handler/initialize";

export default {
  data() {
    return {
      cardSourceStr: "",
      cardName: "",
      cardSource: "",
      cardType: "",
      cardPath: "",
      handler: null,
      priorityFields: ["name", "creator", "creator_notes", "description", "first_mes"],
      orderedFields: []
    }
  },
  computed: {
    apiDefUrl() {
      return `${APIHOST}/api/archive/v1/${this.cardSource}/def/${this.cardType}/${this.cardPath}`
    }
  },
  async created() {
    // Extract query parameters
    this.cardSource = this.$route.query.source
    this.cardType = this.$route.query.type
    this.cardPath = doubleDecodeUrlParam(this.$route.query.path)

    // Validate parameters
    if (!this.cardSource || !this.cardType || !this.cardPath) {
      this.orderedFields = [{
        key: "Error",
        content: "Invalid Parameters"
      }]
      return
    }

    // Set card name based on source
    if (this.cardSource === "chub") {
      this.cardName = `chub/${this.cardType}/${this.cardPath}`
    }

    try {
      // Fetch card definition from API
      const response = await fetch(this.apiDefUrl);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const cardDataDef = await response.json();

      // Initialize handler and resolve card name
      this.handler = initializeHandler(this.cardSource)
      this.cardName = this.handler.resolveCardNameStr(cardDataDef)
      if (this.handler.prettyName) {
        this.cardSourceStr = `${this.handler.prettyName}: `
      }

      // Assuming main data is under 'data' key
      const mainData = cardDataDef.data || cardDataDef

      // Process and order fields
      this.orderedFields = this.processFields(mainData)

    } catch (error) {
      console.error(error)
      this.orderedFields = [{
        key: "Error",
        content: "Failed to load card definition."
      }]
    }
  },
  methods: {
    toTitleCase,
    /**
     * Orders fields based on priority and appends remaining fields.
     * @param {Object} data - The card definition data.
     * @returns {Array} Ordered list of fields.
     */
    processFields(data) {
      const fields = []
      const processedKeys = new Set()

      // Add priority fields first
      this.priorityFields.forEach(field => {
        if (data.hasOwnProperty(field)) {
          const value = data[field]
          if (Array.isArray(value) && field === "alternate_greetings") {
            fields.push({
              key: field,
              content: this.formatContent(value)
            })
          } else {
            fields.push({
              key: field,
              content: this.formatContent(value)
            })
          }
          processedKeys.add(field)
        }
      })

      // Add remaining fields
      Object.keys(data).forEach(key => {
        if (!processedKeys.has(key)) {
          const value = data[key]
          fields.push({
            key: key,
            content: this.formatContent(value)
          })
          processedKeys.add(key)
        }
      })

      return fields
    },
    formatContent(value) {
      if (value == null || value === "") {
        // Return "None" instead of "null"
        return "<i>None</i>"
      } else if (Array.isArray(value)) {
        // If it's an array, join elements with <hr> between them
        return value.map((item, index) => {
          return index === 0 ? item : `<hr class="m-5 border-black">${item}`
        }).join('')
      } else if (typeof value === 'object') {
        // If it's an object, pretty-print JSON
        return hljs.highlight(
            JSON.stringify(value, null, 2),
            {language: 'json'}
        ).value
      } else {
        return value
      }
    }
  },
  mounted() {
    document.title = `Character Card Archive | Definition Viewer`
  },
}
</script>

<style scoped>
.fields-container {
  display: flex;
  flex-direction: column;
}

.field-box {
  max-height: 500px; /* Adjust the max height as needed */
  overflow: hidden; /* Hide horizontal overflow */
  overflow-y: auto; /* Enable vertical scrolling if content exceeds max-height */
  word-break: break-word; /* Break long words or URLs */
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  text-align: justify;
  margin: 0;
  font-family: sans-serif;
}

code {
  font-family: sans-serif;
}
</style>
