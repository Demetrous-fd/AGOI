<template>
  <div class="container">
    <n-card title="Вход" header-style="text-align: center" size="huge">

      <n-form ref="formRef" :model="formValue" :rules="rules" >

        <n-form-item-row label="Логин" path="username">
          <n-input
              v-model:value="formValue.username"
              placeholder=""
              @keyup.enter="handleValidateClick"
              autofocus
          />
        </n-form-item-row>

        <n-form-item-row label="Пароль" path="password">
          <n-input
              v-model:value="formValue.password"
              type="password"
              show-password-on="click"
              placeholder=""
              @keyup.enter="handleValidateClick"
          />
        </n-form-item-row>

        <n-form-item>
          <n-button ref="submitRef" type="primary" @click="handleValidateClick" block secondary strong>
            Войти
          </n-button>
        </n-form-item>

      </n-form>

    </n-card>
  </div>
</template>

<script>
import {ref} from "vue";
import {useMessage} from "naive-ui";
import {login} from "@/helpers";
import router from "@/router";

export default {
  name: "LoginView",
  setup() {
    const formRef = ref(null)
    const formValue = ref({
      username: '',
      password: ''
    })
    const message = useMessage()
    return {
      formRef,
      formValue,
      rules: {
        username: {
          required: true,
          message: ''
        },
        password: {
          required: true,
          message: ''
        }
      },
      handleValidateClick(e) {
        e.preventDefault();
        formRef.value?.validate(async (errors) => {
          if (!errors) {
            const isLoggedIn = await login(formValue.value.username, formValue.value.password)
            if (isLoggedIn) {
              router.push({name: 'home'})
            }
            else
              message.error("Неверный логин или пароль")
          }
        });
      }
    }
  }
}
</script>

<style scoped>
.n-card {
  max-width: 512px;
}
</style>