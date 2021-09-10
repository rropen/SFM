<template>
  <div class="p-8">
    <p class="text-bold font-bold pb-4">Meeting Efficiency Calculator (MEC)</p>
    <p>
      This web application calculates the cost of meetings based on a number of
      inputs. Upon saving the meeting, it stores that information in a SQL
      database. The goal of this application is not to remove meetings, but to
      put into perspective how much our meetings actually cost.
    </p>
    <br />
    <p>
      This is also a proof of concept for deploying applications into the
      Rolls-Royce Gov cloud. This is the first application deployed to the cloud
      in Rolls-Royce, using modern software development.
    </p>
    <br />
    <blockquote></blockquote>
    <blockquote
      className="relative p-4 text-xl italic border-l-4 bg-rrgrey-200 text-rrgrey-800 border-rrgrey-400 quote"
    >
      <p className="mb-4">
        Ex: If you have a meeting with 20 people for 2 hours how much does that
        cost your company? <br /><br />With the valuation of each employee being
        $140/hr, that meeting will cost 20 * 2hr * 140 = <strong>$5600</strong>.
      </p>
    </blockquote>
  </div>
</template>

<script lang="ts" setup></script>
