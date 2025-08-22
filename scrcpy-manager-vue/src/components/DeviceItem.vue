<template>
  <v-card
    :class="[
      'device-item mb-3',
      isSelected
        ? 'device-item--active bg-primary-lighten-5'
        : 'bg-grey-lighten-5',
    ]"
    variant="flat"
    @click="$emit('select', device)"
  >
    <v-card-text class="pa-3">
      <div class="d-flex align-center">
        <v-avatar
          :color="
            device.platform && device.platform.toLowerCase() === 'android'
              ? 'green-lighten-1'
              : 'blue-lighten-1'
          "
          size="32"
          class="mr-3"
        >
          <v-icon
            color="white"
            size="16"
          >
            {{
              device.platform && device.platform.toLowerCase() === "android"
                ? "mdi-android"
                : "mdi-apple"
            }}
          </v-icon>
        </v-avatar>
        <div class="flex-grow-1">
          <h4 class="text-subtitle-2 mb-1">{{ device.name }}</h4>
          <div class="d-flex align-center">
            <v-chip
              :color="
                device.platform && device.platform.toLowerCase() === 'android'
                  ? 'green'
                  : 'blue'
              "
              size="x-small"
              variant="tonal"
              class="mr-2"
            >
              {{
                device.platform && device.platform.toLowerCase() === "android"
                  ? "Android"
                  : "iOS"
              }}
            </v-chip>
            <span class="text-caption text-grey">
              {{
                device.platform && device.platform.toLowerCase() === "android"
                  ? device.android_version
                  : device.ios_version
              }}
            </span>
          </div>
        </div>
        <div class="text-right">
          <v-chip
            :color="device.active ? 'success' : 'grey-lighten-1'"
            size="small"
            variant="flat"
          >
            {{ device.active ? "Activo" : "Inactivo" }}
          </v-chip>
          <div class="text-caption text-grey mt-1">
            {{ device.serial.slice(-4) }}
          </div>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import { defineProps } from "vue";
  defineProps<{ device: any; isSelected: boolean }>();
</script>

<style scoped>
  .device-item {
    cursor: pointer;
    transition: all 0.2s ease;
    border-radius: 8px;
  }
  .device-item:hover {
    transform: translateX(2px);
  }
  .device-item--active {
    border-left: 3px solid rgb(var(--v-theme-primary));
  }
</style>
