<script lang="ts">
import { defineComponent, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default defineComponent({
  setup() {
    const authStore = useAuthStore()

    const loadScript = (src: string) => {
      const script = document.createElement('script')
      script.type = 'text/javascript'
      script.src = src
      script.id = 'supertokens-script'
      script.onload = () => {
        ;(window as any).supertokensUIInit('supertokensui', {
          appInfo: {
            appName: 'rag-service',
            apiDomain: import.meta.env.VITE_APP_ENDPOINT,
            websiteDomain: import.meta.env.VITE_APP_ENDPOINT,
            apiBasePath: '/api/auth',
            websiteBasePath: '/auth'
          },
          recipeList: [
            (window as any).supertokensUIEmailPassword.init({
              onHandleEvent: async (context: any) => {
                if (context.action === 'SUCCESS') {
                  if (context.isNewRecipeUser && context.user.loginMethods.length === 1) {
                    // TODO: Sign up
                  } else {
                    // TODO: Sign in
                  }
                  await authStore.getMe()
                }
              }
            }),
            /*(window as any).supertokensUIThirdParty.init({
                signInAndUpFeature: {
                    providers: [
                        (window as any).supertokensUIThirdParty.Github.init(),
                        (window as any).supertokensUIThirdParty.Google.init(),
                        (window as any).supertokensUIThirdParty.Facebook.init(),
                        (window as any).supertokensUIThirdParty.Apple.init(),
                    ]
                }
            }),*/
            (window as any).supertokensUISession.init()
          ]
        })
      }
      document.body.appendChild(script)
    }

    onMounted(() => {
      loadScript(
        'https://cdn.jsdelivr.net/gh/supertokens/prebuiltui@v0.48.0/build/static/js/main.81589a39.js'
      )
    })

    onUnmounted(() => {
      const script = document.getElementById('supertokens-script')
      if (script) {
        script.remove()
      }
    })
  }
})
</script>

<template>
  <div id="supertokensui" />
</template>
