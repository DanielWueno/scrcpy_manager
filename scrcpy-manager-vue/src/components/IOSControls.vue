<template>
  <v-card
    variant="flat"
    class="mb-4"
  >
    <v-card-title class="d-flex align-center">
      <v-icon
        color="blue"
        class="mr-2"
        >mdi-apple</v-icon
      >
      <span>Controles iOS</span>
    </v-card-title>
    <v-card-text>
      <v-btn
        color="primary"
        :loading="actionLoading"
        @click="$emit('execute-action', { type: 'dummy-ios' })"
      >
        Ejecutar acción dummy
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import { defineProps } from "vue";
  defineProps<{ device: any; actionLoading: boolean }>();
</script>
