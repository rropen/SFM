<template>
  <div class="p-8">
    <p class="text-bold font-bold pb-4">Software Factory Metrics</p>
    <p>
      This web application provides a way for Rolls-Royce Software Factory to
      track and display it's DORA metrics in accordance with modern DevSecOps
      best practices. This is a requirement of the DoD and key in our digital
      transformation.
    </p>
    <br />
    <a
      href="https://www.devops-research.com/research.html"
      style="text-decoration: underline"
    >
      DORA Metrics Explained</a
    >
    <br />
    <p></p>
    <br />
    <table class="w-1/2 mx-auto border-separate border border-blue-800">
      <thead>
        <tr>
          <th class="border border-blue-600">Software Delivery Metric</th>
          <th class="border border-blue-600 bg-green-600 text-white">Elite</th>
          <th class="border border-blue-600 bg-yellow-400 text-rrgrey-800">
            High
          </th>
          <th class="border border-blue-600 bg-orange-500 text-white">
            Medium
          </th>
          <th class="border border-blue-600 bg-red-600 text-white">Low</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="border border-blue-600 px-2 py-1">
            <b>Deployment Frequency:</b> How often we as an organization
            successfully releases to production
          </td>
          <td class="border border-blue-600 px-2 py-1">
            Multiple deploys per day
          </td>
          <td class="border border-blue-600 px-2 py-1">
            Between once per day and once per week
          </td>
          <td class="border border-blue-600 px-2 py-1">
            Between once per week and once per month
          </td>
          <td class="border border-blue-600 px-2 py-1">
            Between once per month and once every six months
          </td>
        </tr>
        <tr class="bg-emerald-200">
          <td class="border border-blue-600 px-2 py-1">
            <b>Time for Changes:</b> The amount of time it takes a commit to get
            into production
          </td>
          <td class="border border-blue-600 px-2 py-1">Less than one day</td>
          <td class="border border-blue-600 px-2 py-1">
            Between one day and one week
          </td>
          <td class="border border-blue-600 px-2 py-1">
            Between one week and one month
          </td>
          <td class="border border-blue-600 px-2 py-1">
            Between one month and six months
          </td>
        </tr>
        <tr>
          <td class="border border-blue-600 px-2 py-1">
            <b>Time to Restore Service:</b> How long it takes an organization to
            recover from a failure in production
          </td>
          <td class="border border-blue-600 px-2 py-1">Less than one hour</td>
          <td class="border border-blue-600 px-2 py-1">Less than one day</td>
          <td class="border border-blue-600 px-2 py-1">Less than one day</td>
          <td class="border border-blue-600 px-2 py-1">
            Between one week and one month
          </td>
        </tr>
        <tr>
          <td class="border border-blue-600 px-2 py-1">
            <b>Change failure rate:</b> The percentage of deployments causing a
            failure in production
          </td>
          <td class="border border-blue-600 px-2 py-1">0-15%</td>
          <td class="border border-blue-600 px-2 py-1">0-15%</td>
          <td class="border border-blue-600 px-2 py-1">0-15%</td>
          <td class="border border-blue-600 px-2 py-1">46-60%</td>
        </tr>
      </tbody>
    </table>
    <br />
    <blockquote></blockquote>
    <blockquote
      className="relative p-4 text-xl italic border-l-4 bg-rrgrey-200 text-rrgrey-800 border-rrgrey-400 quote"
    >
      <p className="mb-4">
        DORA is a research program providing an independent view into practices
        and capabilities that drive high performance in technology delivery. It
        is also used to compare against industry peers.
      </p>
    </blockquote>
  </div>
</template>

<script lang="ts" setup></script>
