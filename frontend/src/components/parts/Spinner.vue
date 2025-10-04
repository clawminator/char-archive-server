<template>
  <div v-if="showSpinner" class="fixed inset-0 flex justify-center items-center sticky-ui loader"
       data-loader="circle"></div>
</template>

<script>
import 'css-loading';
import {mapState} from 'vuex';

export default {
  name: 'Spinner',
  data() {
    return {}
  },
  computed: {
    ...mapState(['showSpinner'])
  },
  methods: {},
  mounted() {
  },
}
</script>

<style scoped>
</style>