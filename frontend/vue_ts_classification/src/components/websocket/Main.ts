import Observer from './Observer'
import Emitter from './Emitter'
//import _Vue, { PluginObject } from "vue";
import Vue, { PluginObject, VueConstructor } from 'vue';

interface IOptions {
  name?: string
}

const WebSocketPlugin: PluginObject<any> = {

 install (vue: VueConstructor, connection: string, opts = {}) {
    if (!connection) { throw new Error('[vue-native-socket] cannot locate connection') }

    let observer: Observer

    if (opts.connectManually) {
      Vue.prototype.$connect = () => {
        observer = new Observer(connection, opts)
        Vue.prototype.$socket = observer.WebSocket
      }

      Vue.prototype.$disconnect = () => {
        if (observer && observer.reconnection) { observer.reconnection = false }
        if (Vue.prototype.$socket) {
          Vue.prototype.$socket.close()
          delete Vue.prototype.$socket
        }
      }
    } else {
      observer = new Observer(connection, opts)
      Vue.prototype.$socket = observer.WebSocket
    }

    Vue.mixin({
      created () {
        let vm = this
        let sockets = this.$options['sockets']

        this.$options.sockets = new Proxy({}, {
          set (target, key, value) {
            Emitter.addListener(key, value, vm)
            target[key] = value
            return true
          },
          deleteProperty (target, key) {
            Emitter.removeListener(key, vm.$options.sockets[key], vm)
            delete target.key
            return true
          }
        })

        if (sockets) {
          Object.keys(sockets).forEach((key) => {
            this.$options.sockets[key] = sockets[key]
          })
        }
      },
      beforeDestroy () {
        let sockets = this.$options['sockets']

        if (sockets) {
          Object.keys(sockets).forEach((key) => {
            delete this.$options.sockets[key]
          })
        }
      }
    })
  }
}

export default WebSocketPlugin;