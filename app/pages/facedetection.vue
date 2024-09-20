<template>
    <v-app>
      <v-app-bar app color="purple" dark>
        <v-toolbar-title>ระบบตรวจจับบุคคลากร</v-toolbar-title>
      </v-app-bar>
  
      <v-main>
        <v-container>
          <v-btn color="purple" class="mr-2" @click="runFaceDetection">ตรวจสอบใบหน้า</v-btn>
          <v-btn color="black" class="mr-2" @click="runFaceRegistration">ลงทะเบียนใบหน้า</v-btn>
          <v-btn color="red" @click="goToStatusPage">ตรวจสอบสถานะ</v-btn>
  
          <v-card class="mb-4">
            <v-card-title>รายชื่อนักเรียนนักศึกษา</v-card-title>
            <v-divider></v-divider>
  
            <v-data-table :headers="headers" :items="users" item-key="id" class="elevation-1">
              <template v-slot:item.student_id="{ item }">{{ item.student_id }}</template>
              <template v-slot:item.username="{ item }">{{ item.username }}</template>
              <template v-slot:item.group="{ item }">{{ item.group }}</template>
              <template v-slot:item.level="{ item }">{{ item.level }}</template>
              <template v-slot:item.status="{ item }">{{ item.status }}</template>
              <template v-slot:item.actions="{ item }">
                <v-btn class="float-right ml-2" color="black" @click="deleteUser(item)">ลบ</v-btn>
                <v-btn class="float-right" small color="purple" @click="openEditDialog(item)">แก้ไข</v-btn>
              </template>
            </v-data-table>
          </v-card>
  
          <v-dialog v-model="editDialog" max-width="600px">
            <v-card>
              <v-card-title>Edit User</v-card-title>
              <v-card-subtitle>แก้ไขข้อมูลผู้ใช้</v-card-subtitle>
              <v-card-text>
                <v-form ref="editForm" v-model="valid">
                  <v-text-field v-model="editedUser.student_id" label="รหัสนักเรียนนักศึกษา" :rules="[rules.required]" required></v-text-field>
                  <v-text-field v-model="editedUser.username" label="ชื่อ - นามสกุล" :rules="[rules.required]" required></v-text-field>
                  <v-text-field v-model="editedUser.group" label="กลุ่ม" :rules="[rules.required]" required></v-text-field>
                  <v-text-field v-model="editedUser.level" label="ระดับชั้น" :rules="[rules.required]" required></v-text-field>
                  <!-- Handle picture field if needed -->
                </v-form>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn text @click="editDialog = false">Cancel</v-btn>
                <v-btn color="purple" @click="updateUser">Save</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-container>
      </v-main>
    </v-app>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        headers: [
          { title: 'ลำดับ', value: 'id' },
          { title: 'รหัสนักเรียนนักศึกษา', value: 'student_id'},
          { title: 'ชื่อ - นามสกุล', value: 'username'},
          { title: 'กลุ่ม', value: 'group' },
          { title: 'ระดับชั้น', value: 'level' },
          { text: 'Actions', value: 'actions', sortable: false }
        ],
        users: [],
        editDialog: false,
        editedUser: {},
        valid: true,
        rules: {
          required: v => !!v || 'Required.',
          email: v => /.+@.+\..+/.test(v) || 'E-mail must be valid.',
          min: v => v.length >= 5 || 'Min 5 characters',
        },
      };
    },
    methods: {
      async fetchUsers() {
        try {
          const response = await axios.get('http://localhost:7000/api/users');
          this.users = response.data;
        } catch (error) {
          console.error('Error fetching users:', error);
        }
      },
      async runFaceDetection() {
        try {
          const response = await axios.get('http://localhost:7000/run-python');
          console.log('Face Detection Response:', response.data);
        } catch (error) {
          console.error('Error running face detection:', error);
        }
      },
      async runFaceRegistration() {
        try {
          const response = await axios.get('http://localhost:7000/run-python2');
          console.log('Face Registration Response:', response.data);
        } catch (error) {
          console.error('Error running face registration:', error);
        }
      },
      goToStatusPage() {
        this.$router.push('/checkstatus');
      },
      openEditDialog(user) {
        this.editedUser = { ...user }; // Copy user data to editedUser
        this.editDialog = true; // Open the dialog
      },
      async updateUser() {
        if (this.$refs.editForm.validate()) {
          try {
            await axios.put(`http://localhost:7000/api/users/${this.editedUser.id}`, {
              student_id: this.editedUser.student_id,
              username: this.editedUser.username,
              group: this.editedUser.group,
              level: this.editedUser.level,
              // Remove picture field if not used
              status: this.editedUser.status,
            });
            this.editDialog = false; // Close the dialog
            this.fetchUsers(); // Refresh the user list
          } catch (error) {
            console.error('Error updating user:', error);
          }
        }
      },
      async deleteUser(user) {
        const confirmDelete = confirm('Are you sure you want to delete this user?');
        if (confirmDelete) {
          try {
            await axios.delete(`http://localhost:7000/api/users/${user.id}`);
            this.fetchUsers(); // Refresh the list after deletion
          } catch (error) {
            console.error('Error deleting user:', error);
          }
        }
      }
    },
    created() {
      this.fetchUsers(); // Fetch users when the component is created
    }
  };
  </script>
  
  <style scoped>
  /* Add any scoped CSS here for styling */
  </style>
  