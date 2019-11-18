import store from './store';

function show(id, message) {
  const current = store.getters.loading || [];
  store.commit('loading', current.concat([{ message }]));
}

function hide(id) {
  const current = store.getters.loading || [];
  const keeps = current.filter(item => id !== null && id !== item.id);
  store.commit('loading', keeps);
}

export default { show, hide };
