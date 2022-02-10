<template>
  <!-- Static sidebar for desktop -->
  <div class="hidden md:flex md:flex-shrink-0">
    <div class="flex flex-col w-64">
      <!-- Sidebar component, swap this element with another sidebar if you like -->
      <div class="flex-1 flex flex-col min-h-0 shadow-md">
        <div class="flex-1 flex flex-col pb-4 overflow-y-auto">
          <h1
            class="
              mx-auto
              text-center
              mt-5
              text-2xl
              font-semibold
              text-rrgrey-800
            "
          >
            DORA<br />Metrics
          </h1>
          <p class="mx-auto mt-2 text-center text-rrblue-800 underline text-sm">
            Learn More
          </p>
          <nav class="mt-5 flex-1 px-2 bg-white space-y-1">
            <h1 class="flex justify-center">test</h1>
            <!-- <LoadingModal v-else /> -->
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineComponent } from "vue";
import { useClient, useQuery, defaultPlugins } from "villus";

const authPlugin = ({ opContext }) => {
  opContext.headers.Authorization = "";
};

useClient({
  url: "https://api.github.com/graphql",
  use: [authPlugin, ...defaultPlugins()],
});
const getData = `query {
  organization(login: "rropen") {
    repositories(first: 100, orderBy: {field: NAME, direction: ASC}) {
      edges {
        node {
          name
        }
      }
    }
  }
}`;
const { data } = useQuery({
  query: getData,
});
console.log(data.value);
</script>
