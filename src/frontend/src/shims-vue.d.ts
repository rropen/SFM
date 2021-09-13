declare module "*.vue" {
  import type { DefineComponent } from "vue";
  import "pinia";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
