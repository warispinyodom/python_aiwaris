<template>
  <v-app>
    <v-container fluid class="fill-height d-flex align-center justify-center">
      <v-card class="pa-6" min-width="400" elevation="2" style="width: 30%;">
        <v-card-title class="text-h5 text-center">Login</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="login">
            <v-text-field
              label="Username"
              v-model="username"
              required
              outlined
              dense
            ></v-text-field>
            <v-text-field
              label="Password"
              v-model="password"
              type="password"
              required
              outlined
              dense
            ></v-text-field>
            <v-btn color="primary" block @click="login">Login</v-btn>
            <v-alert v-if="errorMessage" type="error" class="mt-4">{{ errorMessage }}</v-alert>
          </v-form>
        </v-card-text>
      </v-card>
    </v-container>
  </v-app>
</template>

<script>
import axios from 'axios';


export default {
  data() {
    return {
      username: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://localhost:7000/api/login', {
          username: this.username,
          password: this.password
        });

        if (response.data.message === 'Login successful') {
          this.$router.push('/facedetection'); // Redirect to FaceDetection page
        }
      } catch (error) {
        this.errorMessage = error.response.data.message;
      }
    }
  }
};
</script>

<style scoped>
.fill-height {
  height: 100vh; /* Ensures the container takes full viewport height */
}
.d-flex {
  display: flex; /* Uses Flexbox layout */
}
.align-center {
  align-items: center; /* Centers items vertically */
}
.justify-center {
  justify-content: center; /* Centers items horizontally */
}
</style>
