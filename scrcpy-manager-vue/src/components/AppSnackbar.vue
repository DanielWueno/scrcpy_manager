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
        v-if="actionLabel"
        color="white"
        variant="outlined"
        size="small"
        class="mr-1"
        @click="
          onAction?.();
          close();
        "
      >
        {{ actionLabel }}
      </v-btn>
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
  defineProps<{
    show: boolean;
    message: string;
    color?: string;
    timeout?: number;
    actionLabel?: string;
    onAction?: () => void;
  }>();
  const emit = defineEmits(["update:show"]);
  const close = () => emit("update:show", false);
</script>
