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
    <blockquote></blockquote>
    <blockquote
      className="relative p-4 text-xl italic border-l-4 bg-rrgrey-200 text-rrgrey-800 border-rrgrey-400 quote"
    >
      <p className="mb-4">
        DORA is a research program providing an independent view into practices
        and capabilities that drive high performance in technology delivery. It
        is also used to compare against industry peers.
      </p>
      <p>
        <b>Deployment Frequency:</b> How often we as an organization
        successfully releases to production - Elite: Multiple deploys per day -
        High: Between once per day and once per week - Medium: Between once per
        week and once per month - Low: Between once per month and once every six
        months **Lead
        <br />
        <b>Time for Changes:</b> The amount of time it takes a commit to get
        into production - Elite: Less than one day - High: Between one day and
        one week - Medium: Between one week and one month - Low: Between one
        month and six months
        <br />
        <b>Time to Restore Service:</b> How long it takes an organization to
        recover from a failure in production - Elite: Less than one hour - High:
        Less than one day - Medium: Less than one day - Low: Between one week
        and one month
        <br />
        <b>Change failure rate:</b> The percentage of deployments causing a
        failure in production - Elite: 0-15% - High: 0-15% - Medium: 0-15% -
        Low: 46-60%
      </p>
    </blockquote>
  </div>
</template>

<script lang="ts" setup></script>
