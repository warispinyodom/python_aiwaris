<template>
    <v-app>
        <v-app-bar app color="purple" dark>
            <v-toolbar-title>ตรวจสอบสถานะ</v-toolbar-title>
        </v-app-bar>

        <v-main>
            <v-container>
                <v-btn color="red">
                    <a style="color:white; text-decoration: none;" href="facedetection">กลับไปหน้าแรก</a>
                </v-btn>

                <v-card class="mb-4">
                    <v-card-title>รายงานการเข้าหรือออก</v-card-title>
                    <v-divider></v-divider>

                    <!-- Table to display passes from database -->
                    <v-data-table :headers="headers" :items="passes" item-key="id" class="elevation-1">
                        <!-- Add a new template for displaying the image -->
                        <template v-slot:item.image_path="{ item }">
                            <!-- Construct the image URL -->
                            <v-img :src="`http://localhost:7000/images/${item.image_path}`" max-height="100" max-width="100"></v-img>
                        </template>
                        <template v-slot:item.actions="{ item }">
                            <!-- View button -->
                            <v-btn class="float-right mr-2" small color="purple" @click="viewPass(item)">
                                ดู
                            </v-btn>

                            <!-- Delete button -->
                            <v-btn class="float-right mr-2" small color="black" @click="deletePass(item)">
                                ลบ
                            </v-btn>
                        </template>
                    </v-data-table>
                </v-card>
            </v-container>
        </v-main>
    </v-app>
</template>

<script>
export default {
    data() {
        return {
            headers: [
                { title: 'ลำดับ', value: 'id' },
                { title: 'ชื่อ', value: 'name' },
                { title: 'วันที่ และ เวลา', value: 'timestamp' },
                { title: 'สถานะ', value: 'direction' },
                { title: 'ภาพบันทึก', value: 'image_path' }, // This is where images are shown
                { text: 'Actions', value: 'actions', sortable: false },
            ],
            passes: [],
        };
    },
    mounted() {
        this.fetchPasses(); // Fetch passes on mount

        // Set interval to fetch passes every 5 seconds
        setInterval(this.fetchPasses, 5000);
    },
    methods: {
        async fetchPasses() {
            try {
                const response = await fetch('http://localhost:7000/api/passes');
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                this.passes = data;
            } catch (error) {
                console.error(`Eyyyrror fetching passes: ${error.message}`);
            }
        },
        async deletePass(pass) {
            const confirmDelete = confirm(`Are you sure you want to delete pass ID ${pass.id}?`);
            if (confirmDelete) {
                try {
                    const response = await fetch(`http://localhost:7000/api/passes/${pass.id}`, {
                        method: 'DELETE',
                    });
                    if (!response.ok) throw new Error('Network response was not ok');
                    const data = await response.json();
                    console.log(data.message || 'Pass deleted successfully');
                    this.fetchPasses(); // Refresh the list
                } catch (error) {
                    console.error(`Error deleting pass: ${error.message}`);
                }
            }
        },
        viewPass(pass) {
            const imageUrl = `http://localhost:7000/images/${pass.image_path}`;
            window.open(imageUrl, '_blank'); // Open the image in a new tab
        },
    },
};
</script>

<style scoped>
/* Add any scoped CSS here for styling */
</style>
