<template>
  <div class="bg-rrgrey-200">
    <div class="w-1/3 mx-auto text-center">
      <img class="mb-8 pt-32 mx-auto" src="../assets/img/risks.png" />
      <h1 class="text-lg font-semibold text-rrgrey-800">
        401 - Unauthorized Access
      </h1>
      <p class="text-rrgrey-800 text-md mt-4">
        You have attempted to access a page for which you are not authorized.<br />Please
        check the password you entered, or return home.
      </p>
      <router-link :to="{ name: 'Home' }">
        <button
          type="submit"
          class="
            mt-8
            mb-16
            delay-100
            duration-200
            bg-rrblue-400
            hover:bg-rrblue-200
            text-white
            font-semibold
            py-2
            px-8
            rounded-md
            text-md
            focus:outline-none
          "
        >
          Go Home
        </button>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style></style>
