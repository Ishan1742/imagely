<template>
  <div id="app">
    <input type="text" v-model="hello" />
    <hr />
    {{ hello }}
    <hr />
    <div v-for="(image,index) in images" :key=index>
      {{ image }}
      <hr />
    </div>
  </div>
</template>

<script>
export default {
  name: "App",
  components: {},
  data() {
    return {
      hello: "world",
      images: {},
    };
  },
  async mounted() {
    await this.get();
  },
  methods: {
    async get() {
      let response = await fetch("http://localhost:5000/images");
      let data = await response.json();
      this.images = data;
    },
  },
};
</script>

<style>
</style>
