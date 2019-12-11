import store from './store';

function show(id, message) {
  const current = store.getters.loadingMessages || [];
  store.commit('loadingMessages', current.concat([{ id, message }]));
}

function hide(id) {
  const keeps = (store.getters.loadingMessages || [])
    .filter(item => id !== null && id !== item.id);
  store.commit('loadingMessages', keeps);
}

export default { show, hide };
