<template>
  <router-view v-slot="{ Component }">
    <keep-alive>
      <component :is="Component"/>
    </keep-alive>
  </router-view>
</template>

<script>
import axios from "axios";
import {APIHOST} from "@/components/config";

export default {
  name: 'App',
  methods: {
    async checkBackendHealth() {
      try {
        let apiRes = await axios.get(`${APIHOST}/api/client/msg`)
        let apiStatusCode = apiRes.status
        if (apiStatusCode !== 200) {
          console.error("Got bad status code:", apiStatusCode)
        } else {
          if (apiRes.data != null) {
            if (apiRes.data.msg_type === "status") {
              const statusStr = `<strong>${apiRes.data.title}.</strong> ${apiRes.data.message}`
              this.$store.commit('addStatus', statusStr)
            }
          }
        }
      } catch (err) {
        console.error(`Failed to check messages: ${err}`)
      }
    },
    async checkLocationAndTerms() {
      try {
        const response = await axios.get(`${APIHOST}/api/archive/v1/white-ethnostate/check`)
        if (response.data && response.data.isFromAfrica === true) {
          const acceptedTerms = this.getCookie('i_am_a_nigger')
          if (!acceptedTerms || acceptedTerms !== 'true') {
            window.location = `${APIHOST}/api/archive/v1/white-ethnostate/agreement`
          } else {
            console.log("Nigger has agreed to be on his best behavior. Allowed access.")
          }
        } else {
          // console.log("User is not a nigger, allowing access.")
        }
      } catch (err) {
        console.error(`Failed to check location and terms: ${err}`)
      }
    },
    getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) {
        return parts.pop().split(';').shift();
      }
      return null;
    }
  },
  // beforeRouteEnter(to, from, next) {
  //   next(vm => {
  //   });
  // },
  // async beforeRouteUpdate(to, from, next) {
  //   next()
  // },
  async created() {
    await this.checkBackendHealth()
    await this.checkLocationAndTerms()
    // this.healthCheckInterval = setInterval(this.checkBackendHealth, 60000)
  },
}
</script>
