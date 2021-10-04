<template>
  <div class="bg-rrblue-800 min-h-full overflow-auto">
    <div id="app" class="h-full font-sans bg-rrgrey-200" style="top: 50%">
      <rrHeader
        :appTitleShort="appTitleShort"
        :appTitleLong="appTitleLong"
        :tabsText="tabsText"
        :tabLinks="tabLinks"
      />
      <div class="page bg-rrgrey-200 h-full">
        <router-view />
      </div>
      <rrFooter appTitle="SFM" :appText="appText" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { rrHeader } from "@rrglobal/vue-cobalt";
import { rrFooter } from "@rrglobal/vue-cobalt";
import { computed } from "vue";
import { useRoute } from "vue-router";

const appText =
  "SFM (Software Factory Metrics) is an app to present DevOps metrics for the various applications being built throughout the Software Factory.  These include metrics such as Deployment Frequency which can give insights into the health of the software delivery processes at work and business value delivery in the greater Software Value Stream.";
const route = useRoute();

const appTitleShort = "SFM";
const appTitleLong = "Software Factory Metrics";
const tabsText = ["About"];

const tabLinks = ["About"];

const pathName = computed(() => route.name);
</script>
<style></style>
