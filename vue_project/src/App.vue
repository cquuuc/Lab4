<template>
  <div id="app" class="hide-scrollbar">
    <!-- <img alt="Vue logo" src="./assets/logo.png" /> -->
    <!-- <h1>{{ message }}</h1> -->
    <!-- <p>Request URL: {{ requestUrl }}</p> -->
    <!-- <p>{{ data }}</p> -->
    <el-form
      :inline="true"
      :model="formInline"
      ref="formInline"
      class="demo-form-inline"
    >
      <el-form-item label="">
        <el-input v-model="formInline.capital" placeholder="capital"></el-input>
      </el-form-item>
      <el-form-item label="">
        <el-input v-model="formInline.country" placeholder="country"></el-input>
      </el-form-item>
      <el-form-item label="">
        <el-input
          v-model="formInline.longitude"
          placeholder="longitude"
        ></el-input>
      </el-form-item>
      <el-form-item label="">
        <el-input
          v-model="formInline.latitude"
          placeholder="latitude"
        ></el-input>
      </el-form-item>

      <el-form-item>
        <el-button :disabled="isAdding" type="primary" @click="add"
          >New</el-button
        >
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="loadData"
          >Update</el-button
        >
      </el-form-item>
    </el-form>
    <el-divider></el-divider>
    <el-table
      :data="paginatedData"
      style="width: 100%"
      max-height="80vh"
      v-loading="loading"
      :default-sort="{ prop: 'temperature', order: 'descending' }"
    >
      <el-table-column label="city">
        <template slot-scope="scope">
          <i class="el-icon-time"></i>
          <span style="margin-left: 10px">{{ scope.row.city }}</span>
        </template>
      </el-table-column>
      <el-table-column label="country">
        <template slot-scope="scope">
          <i class="el-icon-time"></i>
          <span style="margin-left: 10px">{{ scope.row.country }}</span>
        </template>
      </el-table-column>
      <el-table-column sortable prop="temperature" label="temperature">
        <template slot-scope="scope">
          <el-popover trigger="hover" placement="top">
            <p>
              Create：<el-tag type="success">{{ scope.row.created_at }}</el-tag>
            </p>
            <p>
              Update：
              <el-tag type="danger" effect="plain">{{
                scope.row.updated_at
              }}</el-tag>
            </p>
            <div slot="reference" class="name-wrapper">
              <el-tag size="medium">{{ scope.row.temperature }}°C</el-tag>
            </div>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column label="Action">
        <template slot-scope="scope">
          <!-- <el-button size="mini" @click="handleEdit(scope.$index, scope.row)"
            >编辑</el-button
          > -->
          <el-button
            size="mini"
            type="danger"
            @click="handleDelete(scope.$index, scope.row)"
            >Delete</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="data.length"
      layout="total, prev, pager, next, jumper"
    ></el-pagination>
  </div>
</template>

<script>
// const comurl = "http://localhost:8000";
// // const comurl = "https://lab4-3z1m.onrender.com";
const comurl = process.env.VUE_APP_API_URL;
async function fetchData(method, url, body = null) {
  const options = {
    method: method, // 请求方法
    headers: {
      "Content-Type": "application/json", // 设置请求头
    },
  };

  // 如果是 POST DELETE 请求，添加请求体
  if (method !== "GET" && body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json(); // 返回 JSON 数据
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error; // 抛出错误以便在调用时处理
  }
}
export default {
  data() {
    return {
      message: "",
      requestUrl: "",
      data: [],
      loading: true,
      formInline: {
        capital: "",
        country: "",
        longitude: "",
        latitude: "",
      },
      isAdding: false, // 控制按钮状态
      currentPage: 1, // 当前页码
      pageSize: 8, // 每页显示的条目数
    };
  },
  mounted() {
    this.loadData();
  },
  computed: {
    paginatedData() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.data.slice(start, end); // 返回当前页的数据
    },
  },
  methods: {
    handleCurrentChange(page) {
      this.currentPage = page; // 更新当前页码
    },
    async loadData() {
      this.loading = true;
      try {
        const result = await fetchData("GET", comurl + "/F5");
        this.message = result.message; // 从响应中获取message
        this.requestUrl = result.request; // 从响应中获取requestUrl
        this.notifysuc(this.message, this.requestUrl);
        console.log(result);

        // this.data = result.data; // 从响应中获取data
        // 对数据按照 temperature 升序排序
        this.data = result.data.sort((a, b) => b.temperature - a.temperature);
        this.currentPage = 1; // 重置当前页码
      } catch (error) {
        // 处理错误
        // this.notifyfail("错误", "数据加载失败");
        this.notifyfail("Eorr", "Data loading failure");
      } finally {
        this.set_loda();
      }
    },

    async postData(url, body) {
      this.loading = true;
      try {
        // const body = this.formInline;
        const result = await fetchData("POST", comurl + url, body);
        console.log(result);

        this.data = [result.data, ...this.data];
        // 处理返回的数据
        // this.notifysuc("成功", "数据已成功提交");
        this.notifysuc("Succ", "submitted successfully");
      } catch (error) {
        // 处理错误
        // this.notifyfail("错误", "数据提交失败");
        this.notifyfail("Eorr", "submitted failure");
      } finally {
        this.set_loda();
        // 无论成功与否都要关闭 loading
      }
    },
    async handleDelete(index, row) {
      this.loading = true;
      try {
        const result = await fetchData("DELETE", comurl + "/delete", {
          city: row.city,
          country: row.country,
        });
        // 从 data 中移除已删除的项
        this.data = this.data.filter(
          (item) => item.city !== row.city || item.country !== row.country
        );
        console.log(result);
        // this.notifysuc("成功", "数据已成功删除");
        this.notifysuc("Succ", "deleted successfully");
      } catch (error) {
        // this.notifyfail("错误", "数据删除失败");
        this.notifyfail("Eorr", "deleted failure");
      } finally {
        this.set_loda();
      }
    },
    add() {
      if (this.isAdding) return; // 防止重复提交
      this.isAdding = true;

      const hasEmpty = Object.values(this.formInline).some(
        (value) => value == ""
      );
      if (hasEmpty) {
        this.notifyfail("错误", "请填写所有字段");
        this.isAdding = false; // 恢复状态
        return;
      }

      let { longitude, latitude } = this.formInline;
      // 验证经度
      if (isNaN(longitude) || longitude < -180 || longitude > 180) {
        this.notifyfail("错误", "经度必须在 -180 到 180 之间");
        this.isAdding = false; // 恢复状态
        return;
      }

      // 验证纬度
      if (isNaN(latitude) || latitude < -90 || latitude > 90) {
        this.notifyfail("错误", "纬度必须在 -90 到 90 之间");
        this.isAdding = false; // 恢复状态
        return;
      }

      // 继续处理表单提交
      this.postData("/add", this.formInline).finally(() => {
        this.isAdding = false; // 恢复状态
      });
    },

    notifysuc(title, message) {
      this.$notify({
        title,
        message,
        type: "success",
        // duration: 0,
        position: "bottom-right",
      });
    },
    notifyfail(title, message) {
      this.$notify({
        title,
        message,
        type: "error",
        position: "bottom-right",
      });
    },
    set_loda() {
      setTimeout(() => {
        this.loading = false; // 无论成功与否都要关闭 loading
      }, 1000);
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
#app {
  display: flex;
  flex-direction: column;
  /* align-items: center; 水平居中 */
  justify-content: center; /* 垂直居中 */
  /* height: 100vh; 使容器占满整个视口高度  */
}

.el-table {
  flex: 1; /* 使表格在容器中弹性伸缩 */
  min-width: 600px; /* 设置最小宽度 */
}
</style>
