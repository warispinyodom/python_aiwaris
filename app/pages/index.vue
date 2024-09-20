<template>
    <div>
      <p>Redirecting to login...</p>
    </div>
  </template>
  
  <script>
  export default {
    mounted() {
      // Redirect to the login page when the component is mounted
      window.location.href = 'Login';
    }
  }
  </script>
  
  <style scoped>
  /* Add any scoped CSS here */
  </style>
  