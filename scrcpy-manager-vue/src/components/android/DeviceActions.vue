<template>
  <v-card variant="outlined">
    <v-card-subtitle class="pb-2">
      <v-icon
        class="mr-1"
        size="16"
        >mdi-gamepad</v-icon
      >
      Controles del Dispositivo
    </v-card-subtitle>
    <v-card-text class="pt-0">
      <v-row dense>
        <v-col cols="12">
          <v-btn
            color="orange"
            variant="outlined"
            :loading="actionLoading"
            :disabled="actionLoading"
            size="large"
            block
            @click="$emit('execute-action', 'wake_device')"
          >
            <v-icon class="mr-2">mdi-power</v-icon>
            Encender Pantalla
          </v-btn>
        </v-col>
        <v-col cols="4">
          <v-btn
            color="info"
            variant="outlined"
            :loading="actionLoading"
            :disabled="actionLoading"
            size="large"
            block
            @click="$emit('execute-action', 'home_button')"
          >
            <v-icon>mdi-home</v-icon>
          </v-btn>
        </v-col>
        <v-col cols="4">
          <v-btn
            color="info"
            variant="outlined"
            :loading="actionLoading"
            :disabled="actionLoading"
            size="large"
            block
            @click="$emit('execute-action', 'back_button')"
          >
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
        </v-col>
        <v-col cols="4">
          <v-btn
            color="success"
            variant="outlined"
            :loading="actionLoading"
            :disabled="actionLoading"
            size="large"
            block
            @click="$emit('execute-action', 'screenshot')"
          >
            <v-icon>mdi-camera</v-icon>
          </v-btn>
        </v-col>
        <v-col cols="6">
          <v-btn
            color="grey"
            variant="outlined"
            :loading="actionLoading"
            :disabled="actionLoading"
            size="large"
            block
            @click="$emit('execute-action', 'volume_up')"
          >
            <v-icon class="mr-2">mdi-volume-plus</v-icon>
            Vol +
          </v-btn>
        </v-col>
        <v-col cols="6">
          <v-btn
            color="grey"
            variant="outlined"
            :loading="actionLoading"
            :disabled="actionLoading"
            size="large"
            block
            @click="$emit('execute-action', 'volume_down')"
          >
            <v-icon class="mr-2">mdi-volume-minus</v-icon>
            Vol -
          </v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>
<script setup lang="ts">
  const props = defineProps<{ actionLoading: boolean }>();
</script>
