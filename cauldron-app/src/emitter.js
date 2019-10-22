import Vue from 'vue';

const bus = new Vue();

function $on(event, callback) {
  return bus.$on(event, callback);
}

function $off(event, callback) {
  return bus.$off(event, callback);
}

function $emit(event, ...args) {
  return bus.$emit(event, ...args);
}

export default { $on, $off, $emit };
