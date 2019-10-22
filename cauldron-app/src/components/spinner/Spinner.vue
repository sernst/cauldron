<template lang="pug">
  .Spinner
    svg.Spinner__box(
      xmlns="http://www.w3.org/2000/svg"
      :width="size"
      :height="size"
    )
      circle.Spinner__path(
        :class="themingClasses"
        fill="none"
        stroke-linecap="round"
        :stroke-width="thickness"
        :cx="half"
        :cy="half"
        :r="radius"
      )
</template>

<script>
function extent() {
  return this.size;
}

function half() {
  return Math.floor(this.size / 2);
}

function radius() {
  return this.half - this.thickness;
}

function thickness() {
  return Math.max(2, Math.floor(6 * Math.min(1, this.size / 60)));
}

function themingClasses() {
  return `Spinner__path--${this.theme}`;
}

export default {
  name: 'Spinner',
  props: {
    size: { type: Number, default: 40 },
    theme: { type: String, default: 'light' },
  },
  computed: {
    extent,
    half,
    radius,
    thickness,
    themingClasses,
  },
};
</script>

<style scoped lang="scss">
  $offset: 187;
  $duration: 1.4s;

  .Spinner {
    display: flex;
    align-items: center;
    justify-content: center;

    &__box {
      animation: rotator $duration linear infinite;
    }

    &__path {
      stroke-dasharray: $offset;
      stroke-dashoffset: 0;
      transform-origin: center;

      &--light {
        animation:
          dash $duration ease-in-out infinite,
          dark-gray-colors ($duration*4) ease-in-out infinite;
      }

      &--dark {
        animation:
          dash $duration ease-in-out infinite,
          light-gray-colors ($duration*4) ease-in-out infinite;
      }
    }
  }

  @keyframes rotator {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(270deg); }
  }

  @keyframes dark-gray-colors {
    0% { stroke: rgba(0, 0, 0, 0.2); }
    20% { stroke: rgba(0, 0, 0, 0.05); }
    40% { stroke: rgba(0, 0, 0, 0.2); }
    60% { stroke: rgba(0, 0, 0, 0.05); }
    80% { stroke: rgba(0, 0, 0, 0.2); }
    100% { stroke: rgba(0, 0, 0, 0.05); }
  }

  @keyframes light-gray-colors {
    0% { stroke: rgba(255, 255, 255, 0.8); }
    20% { stroke: rgba(255, 255, 255, 0.25); }
    40% { stroke: rgba(255, 255, 255, 0.8); }
    60% { stroke: rgba(255, 255, 255, 0.25); }
    80% { stroke: rgba(255, 255, 255, 0.8); }
    100% { stroke: rgba(255, 255, 255, 0.25); }
  }

  @keyframes dash {
    0% { stroke-dashoffset: $offset; }
    50% {
      stroke-dashoffset: $offset/4;
      transform:rotate(135deg);
    }
    100% {
      stroke-dashoffset: $offset;
      transform:rotate(450deg);
    }
  }
</style>
