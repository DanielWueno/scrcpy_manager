<template>
  <v-snackbar
    :model-value="show"
    :color="color"
    :timeout="timeout"
    location="top right"
    variant="flat"
    @update:model-value="emit('update:show', $event)"
  >
    {{ message }}
    <template #actions>
      <v-btn
        color="white"
        variant="text"
        size="small"
        @click="close"
      >
        <v-icon size="16">mdi-close</v-icon>
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script setup lang="ts">
  import { defineProps, defineEmits } from "vue";
  const props = defineProps<{
    show: boolean;
    message: string;
    color?: string;
    timeout?: number;
  }>();
  const emit = defineEmits(["update:show"]);
  const close = () => emit("update:show", false);
</script>
