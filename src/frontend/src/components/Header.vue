<!-- This example requires Tailwind CSS v2.0+ -->
<template>
  <Disclosure as="nav" class="bg-rrblue-800 shadow" v-slot="{ open }">
    <div class="max-w-7xl mr-auto px-6">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <img
              class="block w-8 h-auto"
              src="../assets/img/monogram.jpg"
              alt="Workflow"
            />
            <router-link class="ml-2 md:hidden" :to="{ name: 'Home' }"
              ><div
                class="
                  text-xl
                  leading-16
                  no-underline
                  text-white
                  hover:text-white
                  mr-6
                  font-sans
                "
              >
                SFM
              </div></router-link
            >
            <!-- <img
              class="hidden lg:block h-8 w-auto"
              src="https://tailwindui.com/img/logos/workflow-logo-indigo-600-mark-gray-800-text.svg"
              alt="Workflow"
            /> -->
          </div>
          <div class="hidden sm:ml-2 sm:flex">
            <!-- Current: "border-indigo-500 text-gray-900", Default: "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700" -->
            <router-link class="hidden md:block" :to="{ name: 'Home' }"
              ><div
                class="
                  text-xl
                  leading-16
                  no-underline
                  text-white
                  hover:text-white
                  mr-6
                  font-sans
                "
              >
                Software Factory Metrics
              </div></router-link
            >
            <router-link :to="{ name: 'Dora' }"
              ><div
                class="
                  h-full
                  w-auto
                  leading-16
                  px-4
                  text-md
                  inline-block
                  no-underline
                  text-white
                  hover:text-white hover:bg-rrblue-400
                "
              >
                Dora
              </div></router-link
            >
            <router-link :to="{ name: 'Flow' }"
              ><div
                class="
                  h-full
                  w-auto
                  leading-16
                  px-4
                  text-md
                  inline-block
                  no-underline
                  text-white
                  hover:text-white hover:bg-rrblue-400
                "
              >
                Flow
              </div></router-link
            >
            <router-link :to="{ name: 'About' }"
              ><div
                class="
                  h-full
                  w-auto
                  leading-16
                  px-4
                  text-md
                  inline-block
                  no-underline
                  text-white
                  hover:text-white hover:bg-rrblue-400
                "
              >
                About
              </div></router-link
            >
          </div>
        </div>

        <div class="-mr-2 flex items-center sm:hidden">
          <!-- Mobile menu button -->
          <DisclosureButton
            class="
              inline-flex
              items-center
              justify-center
              p-2
              rounded-md
              text-rrgrey-400
              hover:text-rrgrey-800 hover:bg-rrgrey-400
              focus:outline-none
              focus:ring-2
              focus:ring-inset
              focus:ring-rrblue-400
            "
          >
            <span class="sr-only">Open main menu</span>
            <MenuIcon v-if="!open" class="block h-6 w-6" aria-hidden="true" />
            <XIcon v-else class="block h-6 w-6" aria-hidden="true" />
          </DisclosureButton>
        </div>
      </div>
    </div>

    <DisclosurePanel class="sm:hidden w-full mb-4">
      <div class="pt-2 pb-3 pl-4 space-y-1 bg-rrgrey-200 shadow-md">
        <!-- Current: "bg-indigo-50 border-indigo-500 text-indigo-700", Default: "border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700" -->
        <a
          href="#"
          class="
            bg-rrgrey-400
            border-rrblue-400
            text-rrgrey-800
            block
            pl-3
            pr-4
            py-2
            border-l-4
            text-base
            font-medium
          "
          >Dora</a
        >
        <a
          href="#"
          class="
            border-transparent
            text-rrgrey-600
            hover:bg-white hover:border-rrgrey-600 hover:text-rrgrey-800
            block
            pl-3
            pr-4
            py-2
            border-l-4
            text-base
            font-medium
          "
          >Flow</a
        >
        <a
          href="#"
          class="
            border-transparent
            text-rrgrey-600
            hover:bg-white hover:border-rrgrey-600 hover:text-rrgrey-800
            block
            pl-3
            pr-4
            py-2
            border-l-4
            text-base
            font-medium
          "
          >About</a
        >
      </div>
    </DisclosurePanel>
  </Disclosure>
</template>

<script>
import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
} from "@headlessui/vue";
import { BellIcon, MenuIcon, XIcon } from "@heroicons/vue/outline";

export default {
  components: {
    Disclosure,
    DisclosureButton,
    DisclosurePanel,
    Menu,
    MenuButton,
    MenuItem,
    MenuItems,
    BellIcon,
    MenuIcon,
    XIcon,
  },
};
</script>
