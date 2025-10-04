<template>
  <p>
    An advanced search system is provided to help filter out the nonsense. Search results are cached in the browser, so if you think you aren't seeing up-to-date results, please clear your cache.
  </p>
  <br>
  <hr>
  <p>
    <kbd>"star wars" source:chub author:anonymous</kbd>
  </p>
  <p>
    The quoted string (<kbd>"star wars"</kbd>) searches for the exact phrase in the specified order. It will only return results where the phrase appears exactly as provided. If it was un-quoted (just <kbd>star wars</kbd>), it would have searched for items that contain any of the terms and would
    return documents that contain either "star" or "wars", or both. You should quote a string if you're searching for the exact name of a card.
  </p>
  <p>
    Each element in this query is combined with an implicit <kbd>AND</kbd> operator.
  </p>
  <p>
    <kbd>source:chub</kbd> and <kbd>author:anonymous</kbd> are key-value pairs where <kbd>source</kbd> and <kbd>author</kbd> are the keys and <kbd>chub</kbd> and <kbd>anonymous</kbd> are the values. A list of supported keys is below.
  </p>
  <hr>
  <p>
    If your value in a key-value pair has a space, quote it like this: <kbd>name:"han solo"</kbd>
  </p>
  <hr>
  <p>
    Multiple values for a key in a key-value pair should be seperated into seperate keys: <kbd>tags:lightsaber tags:blaster tags:droids</kbd>
  </p>
  <hr>
  <p>
    The keys in key-value pairs are case-sensitive.
  </p>
  <hr>
  <p>
    Boolean operators are fully supported on all aspects of the search. Supported boolean operators: <kbd>AND</kbd>, <kbd>OR</kbd>, <kbd>NOT</kbd>. Case sensitive.
  </p>
  <p>
    You can combine operators. For example, <kbd>tags:car OR NOT tags:plane</kbd> will return items that either have the tag "car" OR do not have the tag "plane". It will return items that have the tag "car" regardless of whether they also have the tag "plane". It will also include items that do not
    have the tag "car", even if they don't have the tag "plane".
  </p>
  <p>
    <kbd>tags:car AND NOT tags:plane</kbd> will return items that have the tag "car" AND do not have the tag "plane". Items that have both tags "car" and "plane" will be excluded and ones that have neither tag will also be excluded.
  </p>
  <p>
    You can exclude strings as well. For example, <kbd>NOT the</kbd> will exclude the word "the". To exclude more than one word, make sure to quote it like <kbd>NOT "the fox went over"</kbd>.
  </p>
  <p>
    You must use the <kbd>AND</kbd> or <kbd>OR</kbd> operators when combining terms. This will work: <kbd>lightsabers AND NOT tags:"star wars"</kbd>. This will not: <kbd>lightsabers NOT tags:"star wars"</kbd>.
  </p>
  <hr>
  <p>
    The comparison option allows you to filter by inequalities. For example, <kbd>token_count &lt; 1000</kbd> will return only cards have more than 1,000 tokens.
  </p>
  <p>
    You can add multiple comparisons using the small red <kbd>+</kbd> button to the right of the interface. You could, for example, use it to return only cards that have a token count between 1,000 and 2,000 by doing <kbd>token_count &lt; 1000</kbd> and <kbd>token_count &gt; 1000</kbd>.
  </p>
  <p>
    You can also filter by dates. Example: <kbd>12 pm june 1 2025</kbd>.
  </p>
  <hr>
  <br>
  <strong>Natural Language Search</strong>
  <p>
    There is experimental support for semantic searching, referred to as a "natrual language search". You can literally type <kbd>Depressed goth GF who
    likes beer</kbd> and the omniscient entity that is le AI will try to give you the most similar characters.
  </p>
  <p>
    Search operators and keys are not applicable to natrual language searches.
  </p>
  <p>
    Unfortunately, it is very expensive to crunch the data for this type of search and I am not able to invest the enourmous amount of time and resources required. So it isn't very accurate.
  </p>
  <hr>
  <br>
  <strong>Character Search Keys</strong>
  <p>These keywords apply to character cards and can also be used in the "Order by Key" or "Comparison" fields.</p>
  <ul>
    <li v-for="(item, index) in characterKeys" :key="`characterKeys-${index}`">
      <kbd>{{ item.name }}</kbd>&nbsp; {{ item.desc }}
    </li>
  </ul>
  <br>
  <strong>Lorebook Search Keys</strong>
  <p>These keywords apply to lorebooks and can also be used in the "Order by Key" or "Comparison" fields.</p>
  <ul>
    <li v-for="(item, index) in lorebookKeys" :key="`lorebookKeys-${index}`">
      <kbd>{{ item.name }}</kbd>&nbsp; {{ item.desc }}
    </li>
  </ul>
  <br>
  <strong>chub.ai Search Keys</strong>
  <p>These keywords apply to chub.ai items.</p>
  <ul>
    <li v-for="(item, index) in chubKeys" :key="`chubKeys-${index}`">
      <kbd>{{ item.name }}</kbd>&nbsp; {{ item.desc }}
    </li>
  </ul>
  <br>
  <strong>Sources</strong>
  <p>These are the values that are valid for the <kbd>source</kbd> keyword.</p>
  <ul>
    <li v-for="(item, index) in sources" :key="`sources-${index}`">
      <kbd>{{ item }}</kbd>
    </li>
  </ul>
  <br>
  <strong>Specific Sources</strong>
  <p>
    These are the values that are valid for the <kbd>sourceSpecific</kbd> keyword. Cards with these specific sources are
    grouped under the <kbd>generic</kbd> source but differentiated through this identifier.
  </p>
  <ul>
    <li v-for="(item, index) in sourcesSpecific" :key="`sourcesSpecific-${index}`">
      <kbd>{{ item }}</kbd>
    </li>
  </ul>
</template>

<script>

import {mapState} from "vuex";

export default {
  name: 'SearchInfo',
  components: {},
  computed: {
    ...mapState(["searchKeys"]),
  },
  data() {
    return {
      characterKeys: [],
      chubKeys: [],
      lorebookKeys: [],
      sources: [],
      sourcesSpecific: [],
    };
  },
  watch: {
    searchKeys: {
      handler(newValue) {
        // Wait for the main search page to fill in this value.
        if (newValue && Object.keys(newValue).length > 0) {
          this.setSearchKeywords();
        }
      },
      deep: true,
      immediate: true,
    },
  },
  methods: {
    setSearchKeywords() {
      this.characterKeys = this.searchKeys.character || [];
      this.chubKeys = this.searchKeys.chub || [];
      this.lorebookKeys = this.searchKeys.lorebook || [];
      this.sources = this.searchKeys.sources?.types || [];
      this.sourcesSpecific = this.searchKeys.sources?.specific || [];
    },
  },
  created() {
  },
};

</script>

<style scoped>

</style>
