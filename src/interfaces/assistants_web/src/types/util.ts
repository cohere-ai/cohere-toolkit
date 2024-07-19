export type NoNullProperties<Type> = {
  [Property in keyof Type]-?: NonNullable<Type[Property]>;
};
