<!-- filepath: c:\Users\DSOFT03.CORP\Documents\Soft\scrcpy_manager\scrcpy-manager-vue\src\components\ConnectionStatus.vue -->
<template>
  <v-card
    v-if="!isApiConnected"
    color="error"
    variant="tonal"
    class="ma-4"
  >
    <v-card-title class="d-flex align-center">
      <v-icon left>mdi-wifi-off</v-icon>
      Backend API No Disponible
    </v-card-title>

    <v-card-text>
      <p class="mb-2">
        No se puede conectar al servidor backend en
        <code>http://127.0.0.1:5000</code>
      </p>

      <v-divider class="my-3" />

      <p class="text-h6 mb-2">Para solucionarlo:</p>
      <ol class="text-body-2">
        <li>Asegúrate de que el servidor backend esté corriendo</li>
        <li>Verifica que esté disponible en el puerto 5000</li>
        <li>Comprueba que no hay un firewall bloqueando la conexión</li>
      </ol>

      <v-btn
        @click="testConnection"
        :loading="testing"
        color="primary"
        variant="outlined"
        class="mt-3"
      >
        <v-icon left>mdi-refresh</v-icon>
        Probar Conexión
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import { ref, onMounted } from "vue";
  import { deviceApi } from "../services/api";

  const isApiConnected = ref(false);
  const testing = ref(false);

  const testConnection = async () => {
    testing.value = true;
    try {
      await deviceApi.getDevices();
      isApiConnected.value = true;
    } catch (error) {
      isApiConnected.value = false;
      console.error("Connection test failed:", error);
    } finally {
      testing.value = false;
    }
  };

  onMounted(() => {
    testConnection();
  });

  defineExpose({
    testConnection,
    isApiConnected,
  });
</script>
